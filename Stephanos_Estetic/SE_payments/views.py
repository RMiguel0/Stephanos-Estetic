# SE_payments/views.py
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import PaymentIntent
from .services import create_payment_for, get_provider
# Ejemplo: supongamos que pagas una Orden (SE_sales.Order)
# from SE_sales.models import Order

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
