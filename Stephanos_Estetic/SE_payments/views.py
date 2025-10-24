# SE_payments/views.py
import uuid
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status as drf_status
from .models import PaymentIntent
from .services import create_payment_for, get_provider
from rest_framework import status
from .webpay_service import create_tx, commit_tx
from datetime import datetime
# Ejemplo: supongamos que pagas una Orden (SE_sales.Order)
# from SE_sales.models import Order



FRONTEND_URL = getattr(settings, "FRONTEND_URL", "http://localhost:5173")

def _to_dt(s: str | None):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None

@api_view(['POST'])
@permission_classes([AllowAny])
def checkout_dummy(request):
    """
    Ejemplo minimal: crea un intent "independiente" para probar el flujo con provider fake.
    En tu proyecto real, esto vendrá desde Order/Booking/Donation.
    """
    amount = int(request.data.get("amount", 1000))
    description = request.data.get("description", "Pago de prueba")
    provider_slug = request.data.get("provider", "fake")

    # return_url apunta a un endpoint que "recibe" al usuario tras pagar
    return_url = request.build_absolute_uri(reverse("payments:return"))
    cancel_url = request.build_absolute_uri(reverse("payments:cancel"))

    # Creamos el intent y obtenemos la URL para redirigir
    # Aquí no tenemos objeto de negocio; podrías crear un dummy o referenciar un ID libre.
    dummy_obj = PaymentIntent()  # HACK: solo para tener ContentType; usa tu Order real
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
    """
    Punto de retorno (la página a la que vuelve el usuario). En provider real, no
    confíes solo en esto; usa WEBHOOK para confirmar de verdad.
    Para fake, marcaremos el pago usando la query 'paid=1'.
    """
    provider = get_provider("fake")  # en real: deducir por intent.provider
    update = provider.handle_webhook(request)  # usamos la misma lógica

    # Resuelve el intent vía parámetro 'intent' (fake lo manda en el querystring)
    intent_id = request.GET.get("intent")
    intent = get_object_or_404(PaymentIntent, pk=intent_id)
    intent.status = update.status
    intent.save(update_fields=["status"])

    # Aquí podrías redirigir a tu frontend (página de éxito/fracaso)
    # Por demo, devolvemos un JSON
    return Response({"status": intent.status, "intent": str(intent.id)})

@api_view(['GET'])
@permission_classes([AllowAny])
def payment_cancel(request):
    return Response({"cancelled": True})

@api_view(["POST"])
@permission_classes([AllowAny])
def webpay_create(request):
    """
    Crea la transacción en Webpay y devuelve url + token.
    amount debe ser entero en CLP (p.ej. 16980).
    """
    try:
        amount = int(request.data.get("amount", 0))
        if amount <= 0:
            return Response({"detail": "Monto inválido"}, status=status.HTTP_400_BAD_REQUEST)

        buy_order = f"ORD-{uuid.uuid4().hex[:10]}"
        session_id = uuid.uuid4().hex

        resp = create_tx(buy_order=buy_order,
                         session_id=session_id,
                         amount=amount,
                         return_url=settings.WEBPAY_RETURN_URL)

        # resp => {"token": "...", "url": "https://webpay3g.transbank.cl/webpayserver/initTransaction"}
        return Response({"url": resp["url"], "token": resp["token"]})
    except Exception as e:
        return Response({"detail": str(e)}, status=500)

@api_view(["POST", "GET"])
@permission_classes([AllowAny])
def webpay_commit(request):
    """
    Punto de retorno/confirmación: Webpay vuelve aquí con token_ws.
    """
    tbk_token = request.data.get("TBK_TOKEN") or request.GET.get("TBK_TOKEN")
    if tbk_token:
        # Si habías creado registro previo, márcalo:
        PaymentIntent.objects.filter(token=tbk_token).update(status=PaymentIntent.Status.ABORTED)
        # Redirige a tu front (cancel):
        return redirect(f"{FRONTEND_URL}/checkout/cancel")



    token = request.data.get("token_ws") or request.GET.get("token_ws")
    if not token:
        return Response({"detail": "token_ws ausente"}, status=status.HTTP_400_BAD_REQUEST)

    result = commit_tx(token)
    status_tx = result.get("status")
    buy_order = result.get("buy_order")
    amount = result.get("amount")

    payment, _ = PaymentIntent.objects.update_or_create(
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
    # 4) (Opcional) valida contra tu Order y márcala pagada
    # if payment.order_id:
    #     order = payment.order
    #     # valida montos
    #     if amount == order.total_amount and status_tx == "AUTHORIZED":
    #         order.status = "PAID"
    #         order.paid_amount = amount
    #         order.save(update_fields=["status", "paid_amount"])

    ok = (status_tx == "AUTHORIZED")

    # 5) decide: JSON (API) o redirección a tu frontend
    # Para SPA es cómodo redirigir a /checkout/success?order=... y ahí mostrar detalle
    return redirect(f"{FRONTEND_URL}/checkout/success?order={buy_order}")

    # Si prefieres JSON (como ahora):
    # return Response({"ok": ok, "result": result})

    
