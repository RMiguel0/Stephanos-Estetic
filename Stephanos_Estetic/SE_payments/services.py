# SE_payments/services.py
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from .models import PaymentIntent
from .adapters.fake import FakeProvider
# from .adapters.webpay import WebpayProvider  # cuando lo implementes

PROVIDERS = {
    "fake": FakeProvider(),
    # "webpay": WebpayProvider(),
}

def get_provider(slug: str):
    try:
        return PROVIDERS[slug]
    except KeyError:
        raise ValueError(f"Proveedor no configurado: {slug}")

def create_payment_for(obj, *, amount: int, description: str,
                       provider_slug: str, return_url: str, cancel_url: str) -> tuple[PaymentIntent, str]:
    """
    Crea el PaymentIntent y devuelve (intent, redirect_url) para el checkout.
    """
    intent = PaymentIntent.objects.create(
        amount=amount,
        description=description,
        provider=provider_slug,
        return_url=return_url,
        cancel_url=cancel_url,
        ref_content_type=ContentType.objects.get_for_model(obj),
        ref_object_id=obj.pk,
    )
    provider = get_provider(provider_slug)
    init = provider.create_checkout(intent, request=None)  # opcional: pasa HttpRequest si lo necesitas
    return intent, init.redirect_url
