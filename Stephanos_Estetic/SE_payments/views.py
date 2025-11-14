# SE_payments/views.py
import uuid
from io import BytesIO
from datetime import datetime
import os

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
from reportlab.lib import colors


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
        return Response({"detail": "Parámetro 'buy_order' es requerido"}, status=400)

    # Buscar el Payment por buy_order
    p = get_object_or_404(PaymentIntent, buy_order=buy_order)

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4

    x_margin = 25 * mm
    header_height = 40 * mm

    # ─────────────────────────────────────────────
    # Header con barra de color + logo + título
    # ─────────────────────────────────────────────
    c.setFillColorRGB(0.94, 0.35, 0.58)  # rosa suave
    c.rect(0, H - header_height, W, header_height, fill=1, stroke=0)

    logo_x = x_margin
    title_x = x_margin
    try:
        logo_path = os.path.join(settings.BASE_DIR, "static", "img", "logo-stephanos.png")
        if os.path.exists(logo_path):
            logo_w = 22 * mm
            logo_h = 22 * mm
            logo_y = H - header_height / 2 - logo_h / 2
            c.drawImage(
                logo_path,
                logo_x,
                logo_y,
                width=logo_w,
                height=logo_h,
                preserveAspectRatio=True,
                mask="auto",
            )
            title_x = logo_x + logo_w + 8 * mm
    except Exception:
        title_x = x_margin

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(title_x, H - 22 * mm, "Stephanos Estetic")
    c.setFont("Helvetica", 11)
    c.drawString(title_x, H - 30 * mm, "Comprobante de pago")

    # ─────────────────────────────────────────────
    # Datos del pago
    # ─────────────────────────────────────────────
    y = H - header_height - 15 * mm
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)

    fecha_pago = timezone.localtime(p.transaction_date or timezone.now())
    c.drawString(x_margin, y, f"Fecha de pago: {fecha_pago:%Y-%m-%d %H:%M}")
    y -= 6 * mm

    c.drawString(x_margin, y, f"Orden: {p.buy_order}")
    y -= 6 * mm

    c.drawString(x_margin, y, f"Estado: {p.status}")
    y -= 6 * mm

    if getattr(p, "authorization_code", None):
        c.drawString(x_margin, y, f"Código de autorización: {p.authorization_code}")
        y -= 6 * mm

    if getattr(p, "card_last4", None):
        c.drawString(x_margin, y, f"Tarjeta: **** **** **** {p.card_last4}")
        y -= 6 * mm

    # Separador
    y -= 6 * mm
    c.setStrokeColor(colors.lightgrey)
    c.line(x_margin, y, W - x_margin, y)
    y -= 8 * mm

    # ─────────────────────────────────────────────
    # Detalle de la compra (concepto + tabla ítems)
    # ─────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_margin, y, "Detalle de la compra")
    y -= 8 * mm
    c.setFont("Helvetica", 10)

    concepto = getattr(
        p,
        "description",
        "Productos y/o servicios adquiridos en Stephanos Estetic",
    )
    c.drawString(x_margin, y, f"Concepto: {concepto}")
    y -= 8 * mm

    # Ítems (Order / Booking según tu modelo)
    items = []
    if getattr(p, "order", None) and hasattr(p.order, "items"):
        items = list(p.order.items.all())
    elif getattr(p, "booking", None):
        items = [p.booking]

    if items:
        y -= 4 * mm
        desc_x = x_margin
        qty_x = W - 80 * mm
        unit_x = W - 55 * mm
        total_x = W - 25 * mm

        c.setFont("Helvetica-Bold", 9)
        c.drawString(desc_x, y, "Descripción")
        c.drawString(qty_x, y, "Cant.")
        c.drawString(unit_x, y, "P. unitario")
        c.drawString(total_x, y, "Subtotal")
        y -= 4 * mm
        c.setStrokeColor(colors.lightgrey)
        c.line(x_margin, y, W - x_margin, y)
        y -= 6 * mm

        c.setFont("Helvetica", 9)

        for it in items:
            # ----- Caso productos: OrderItem -----
            desc = None
            qty = 1
            unit_price = 0
            line_total = 0

            # Importante: OrderItem viene de SE_sales.models (ya está importado arriba)
            try:
                from SE_sales.models import OrderItem  # no pasa nada si se repite
            except Exception:
                OrderItem = None

            if OrderItem is not None and isinstance(it, OrderItem):
                desc = getattr(it.product, "name", str(it))
                qty = it.qty
                unit_price = it.price_at
                line_total = it.line_total

            # ----- Caso servicios: Booking u otro objeto -----
            else:
                # intenta algo razonable para bookings/servicios
                desc = (
                    getattr(it, "service_name", None)
                    or getattr(getattr(it, "service", None), "name", None)
                    or getattr(it, "name", None)
                    or str(it)
                )
                qty = getattr(it, "qty", 1)
                unit_price = (
                    getattr(it, "final_price", None)
                    or getattr(it, "price_at", None)
                    or getattr(it, "price", 0)
                )
                line_total = getattr(it, "line_total", None) or (unit_price * qty)

            # salto de página si estamos muy abajo
            if y < 40 * mm:
                c.showPage()
                c.setFont("Helvetica", 9)
                y = H - 30 * mm
                c.setFont("Helvetica-Bold", 9)
                c.drawString(desc_x, y, "Descripción")
                c.drawString(qty_x, y, "Cant.")
                c.drawString(unit_x, y, "P. unitario")
                c.drawString(total_x, y, "Subtotal")
                y -= 4 * mm
                c.setStrokeColor(colors.lightgrey)
                c.line(x_margin, y, W - x_margin, y)
                y -= 6 * mm
                c.setFont("Helvetica", 9)

            # Fila
            c.drawString(desc_x, y, str(desc)[:60])
            c.drawRightString(qty_x + 10 * mm, y, str(qty))
            c.drawRightString(unit_x + 20 * mm, y, _clp(unit_price))
            c.drawRightString(total_x, y, _clp(line_total))
            y -= 6 * mm

        y -= 4 * mm
        c.setStrokeColor(colors.lightgrey)
        c.line(x_margin, y, W - x_margin, y)
        y -= 10 * mm
    else:
        y -= 12 * mm


    # ─────────────────────────────────────────────
    # Total pagado (caja)
    # ─────────────────────────────────────────────
    box_width = 70 * mm
    box_height = 20 * mm
    box_x = x_margin
    box_y = y - 15 * mm

    c.setFillColorRGB(0.97, 0.9, 0.94)
    c.roundRect(box_x, box_y, box_width, box_height, 4 * mm, fill=1, stroke=0)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(box_x + 4 * mm, box_y + box_height - 7 * mm, "Total pagado")

    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(
        box_x + box_width - 4 * mm,
        box_y + 6 * mm,
        _clp(p.amount),
    )

    # ─────────────────────────────────────────────
    # Footer
    # ─────────────────────────────────────────────
    c.setFillColor(colors.darkgrey)
    c.setFont("Helvetica", 8)
    c.drawString(
        x_margin,
        20 * mm,
        "Este comprobante es válido como respaldo de su pago online.",
    )
    c.drawString(
        x_margin,
        15 * mm,
        "Gracias por confiar en Stephanos Estetic.",
    )

    c.showPage()
    c.save()
    buf.seek(0)

    filename = f"boleta_{p.buy_order}.pdf"
    return FileResponse(
        buf,
        as_attachment=True,
        filename=filename,
        content_type="application/pdf",
    )
