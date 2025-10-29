# SE_payments/views.py
import uuid
from io import BytesIO
from datetime import datetime

from django.http import FileResponse, Http404
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status as drf_status

from .models import PaymentIntent
from .services import create_payment_for, get_provider
from .webpay_service import create_tx, commit_tx
from SE_sales.services import finalize_paid_order
from SE_sales.models import Order, OrderItem, Product

from decimal import Decimal


FRONTEND_URL = getattr(settings, "FRONTEND_URL", "http://localhost:5173")


# ---------- utilidades ----------
def _clp(n: int) -> str:
    return f"${n:,.0f}".replace(",", ".")

def _to_dt(s: str | None):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


# ---------- flujo de prueba (fake provider) ----------
@api_view(['POST'])
@permission_classes([AllowAny])
def checkout_dummy(request):
    """ Flujo de pago fake para pruebas. """
    amount = int(request.data.get("amount", 1000))
    description = request.data.get("description", "Pago de prueba")
    provider_slug = request.data.get("provider", "fake")

    return_url = request.build_absolute_uri(reverse("payments:return"))
    cancel_url = request.build_absolute_uri(reverse("payments:cancel"))

    # HACK: solo para tener ContentType con create_payment_for
    dummy_obj = PaymentIntent()
    dummy_obj.pk = 0

    intent, redirect_url = create_payment_for(
        obj=dummy_obj,
        amount=amount,
        description=description,
        provider_slug=provider_slug,
        return_url=return_url,
        cancel_url=cancel_url,
    )
    return Response({"intent": str(intent.id), "redirect_url": redirect_url})


@api_view(['GET'])
@permission_classes([AllowAny])
def payment_return(request):
    """ Retorno fake para debug. """
    provider = get_provider("fake")
    update = provider.handle_webhook(request)
    intent_id = request.GET.get("intent")
    intent = get_object_or_404(PaymentIntent, pk=intent_id)
    intent.status = update.status
    intent.save(update_fields=["status"])
    return Response({"status": intent.status, "intent": str(intent.id)})


@api_view(['GET'])
@permission_classes([AllowAny])
def payment_cancel(request):
    return Response({"cancelled": True})


# ---------- Webpay: crear transacción ----------
@api_view(["POST"])
@permission_classes([AllowAny])
def webpay_create(request):
    """
    Crea Order + OrderItems desde el carrito, calcula total y abre transacción Webpay.
    Espera payload:
    {
      "items": [{ "product_id": 12, "qty": 2 }, ...]  // id del producto y cantidad
    }
    """
    try:
        payload = request.data or {}
        raw_items = payload.get("items") or []
        if not raw_items:
            return Response({"detail": "Carrito vacío"}, status=drf_status.HTTP_400_BAD_REQUEST)

        # 1) Crear Order básica
        user = request.user if request.user.is_authenticated else None
        order = Order.objects.create(
            user=user,
            customer_name=(getattr(user, "get_full_name", lambda: "")() or "") if user else "",
            customer_email=(getattr(user, "email", "") or "") if user else "",
            status="pending",
        )

        # 2) Agregar OrderItems (precio congelado en price_at)
        # 2) Agregar OrderItems (precio congelado en price_at)
        total = Decimal("0")
        for it in raw_items:
            pid = it.get("product_id") or it.get("id")
            sku = it.get("sku")

            qty = int(it.get("qty", 1))
            if qty <= 0:
                return Response({"detail": "Cantidad inválida"}, status=drf_status.HTTP_400_BAD_REQUEST)

            # Resolver producto por id numérico o por sku
            product = None
            # 2a) si viene id numérico
            if pid is not None:
                try:
                    product = Product.objects.get(pk=int(pid))
                except (ValueError, Product.DoesNotExist):
                    product = None

            # 2b) si no lo encontramos por id, probar por sku (string)
            if product is None:
                key = sku or pid  # por si el front mandó solo "id" pero en realidad era un SKU string
                if not key:
                    return Response({"detail": "Falta product_id o sku"}, status=drf_status.HTTP_400_BAD_REQUEST)
                try:
                    product = Product.objects.get(sku=str(key))
                except Product.DoesNotExist:
                    return Response({"detail": f"Producto no encontrado: {key}"}, status=drf_status.HTTP_400_BAD_REQUEST)

            price_at = product.price  # Decimal
            line_total = (Decimal(qty) * price_at)
            OrderItem.objects.create(
                order=order,
                product=product,
                qty=qty,
                price_at=price_at,
                line_total=line_total,
            )
            total += line_total


        # 3) Guardar total
        order.total_amount = total
        order.save(update_fields=["total_amount"])

        # 4) Crear transacción Webpay
        buy_order = str(order.id)    # ✅ importantísimo!
        session_id = uuid.uuid4().hex
        amount = int(total)          # CLP entero para Webpay

        resp = create_tx(
            buy_order=buy_order,
            session_id=session_id,
            amount=amount,
            return_url=settings.WEBPAY_RETURN_URL,
        )

        # 5) Registrar/actualizar PaymentIntent en PENDING, enlazado a la Order
        PaymentIntent.objects.update_or_create(
            buy_order=buy_order,
            defaults={
                "order": order,
                "token": resp["token"],
                "session_id": session_id,
                "amount": amount,
                "status": PaymentIntent.Status.PENDING,
            },
        )

        return Response({"url": resp["url"], "token": resp["token"]})

    except Product.DoesNotExist:
        return Response({"detail": "Producto no existe"}, status=drf_status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": str(e)}, status=500)


# ---------- Webpay: commit ----------
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
@login_required  # si permites guest, quítalo
def webpay_commit(request):
    """
    Punto de retorno/confirmación: Webpay vuelve aquí con token_ws.
    Maneja abortos con TBK_TOKEN.
    """
    # Abortada por el usuario (Webpay envía TBK_TOKEN)
    tbk_token = request.POST.get("TBK_TOKEN") or request.GET.get("TBK_TOKEN")
    if tbk_token:
        PaymentIntent.objects.filter(token=tbk_token).update(
            status=PaymentIntent.Status.ABORTED
        )
        return redirect(f"{FRONTEND_URL}/checkout/cancel")

    # Confirmación: Webpay envía token_ws
    token = (
        request.POST.get("token_ws")
        or request.data.get("token_ws")
        or request.GET.get("token_ws")
    )
    if not token:
        return Response({"detail": "Missing token_ws"}, status=drf_status.HTTP_400_BAD_REQUEST)


    # 1) Commit en Transbank
    result = commit_tx(token)
    status_tx = result.get("status")
    buy_order = result.get("buy_order")
    amount = result.get("amount")

    # 2) Actualiza/crea PaymentIntent con todos los detalles
    p, _ = PaymentIntent.objects.update_or_create(
        buy_order=buy_order,
        defaults={
            "token": token,
            "session_id": result.get("session_id"),
            "amount": amount,
            "status": status_tx,
            "vci": result.get("vci"),
            "authorization_code": result.get("authorization_code"),
            "accounting_date": result.get("accounting_date"),
            "transaction_date": _to_dt(result.get("transaction_date")),
            "payment_type_code": result.get("payment_type_code"),
            "installments_number": int(result.get("installments_number") or 0),
            "card_last4": (result.get("card_detail") or {}).get("card_number"),
            "raw": result,
        },
    )

    ok = (status_tx == "AUTHORIZED")

    # 3) Si fue autorizado: marca Orden pagada + consume stock + historial (idempotente)
    if ok:
        try:
            if not p.order_id:
                # En principio siempre debería estar seteado desde webpay_create
                # Reintento por si buy_order == id
                try:
                    order = Order.objects.get(pk=int(buy_order))
                    p.order = order
                    p.save(update_fields=["order"])
                except Exception:
                    pass

            if not p.order_id:
                p.status = PaymentIntent.Status.FAILED
                p.save(update_fields=["status"])
                return redirect(f"{FRONTEND_URL}/checkout/success?ok=false&buy_order={buy_order}")

            # Finaliza la orden: stock, status=paid, historial
            finalize_paid_order(p.order_id, request.user)

        except Exception as e:
            p.status = PaymentIntent.Status.FAILED
            p.save(update_fields=["status"])
            return Response({"detail": str(e)}, status=drf_status.HTTP_409_CONFLICT)

    # 4) Redirige al front con resultado (SPA-friendly)
    return redirect(f"{FRONTEND_URL}/checkout/success?ok={str(ok).lower()}&buy_order={buy_order}")


# ---------- Info / comprobantes ----------
@api_view(["GET"])
@permission_classes([AllowAny])
def payment_detail(request):
    buy_order = request.GET.get("buy_order")
    try:
        p = PaymentIntent.objects.get(buy_order=buy_order)
        return Response({
            "buy_order": p.buy_order,
            "amount": p.amount,
            "status": p.status,
            "authorization_code": p.authorization_code,
            "transaction_date": p.transaction_date,
            "card_last4": p.card_last4,
        })
    except PaymentIntent.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)


@api_view(["GET"])
@permission_classes([AllowAny])
def payment_receipt(request):
    buy_order = request.GET.get("buy_order")
    if not buy_order:
        return Response({"detail": "buy_order requerido"}, status=400)
    try:
        p = PaymentIntent.objects.get(buy_order=buy_order)
    except PaymentIntent.DoesNotExist:
        raise Http404("Pago no encontrado")

    # PDF temporal
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4
    x, y = 25*mm, H - 30*mm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, "Boleta de pago (TEST)")
    y -= 10*mm
    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Fecha: {timezone.localtime(p.transaction_date or timezone.now()):%Y-%m-%d %H:%M}")
    y -= 6*mm
    c.drawString(x, y, f"Orden: {p.buy_order}")
    y -= 6*mm
    c.drawString(x, y, f"Estado: {p.status}")
    y -= 6*mm
    if p.authorization_code:
        c.drawString(x, y, f"Código de autorización: {p.authorization_code}")
        y -= 6*mm
    if p.card_last4:
        c.drawString(x, y, f"Tarjeta: **** **** **** {p.card_last4}")
        y -= 6*mm

    y -= 4*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, f"Total pagado: {_clp(p.amount)}")

    c.showPage()
    c.save()
    buf.seek(0)

    filename = f"boleta_{p.buy_order}.pdf"
    return FileResponse(buf, as_attachment=True, filename=filename, content_type="application/pdf")
