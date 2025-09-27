# SE_payments/adapters/fake.py
from __future__ import annotations
from django.http import HttpRequest
from .base import PaymentProvider, PaymentInitResult, PaymentUpdate

class FakeProvider(PaymentProvider):
    """
    Proveedor de prueba:
    - create_checkout: redirige al 'return_url' con parámetros simulados.
    - handle_webhook: usa parámetros de la query para "confirmar" el pago.
    """

    def __init__(self):
        super().__init__(slug="fake")

    def create_checkout(self, intent, request: HttpRequest) -> PaymentInitResult:
        # Simulamos que el gateway nos devuelve una URL para redirigir
        intent.provider_session_id = f"fake-{intent.id}"
        intent.save(update_fields=["provider_session_id"])

        # Redirigimos al return_url con señales simuladas (paid=1)
        # En la vida real, NO confíes en el cliente; aquí es solo para pruebas locales.
        redirect = f"{intent.return_url}?intent={intent.id}&provider=fake&paid=1"
        return PaymentInitResult(redirect_url=redirect, provider_session_id=intent.provider_session_id)

    def handle_webhook(self, request: HttpRequest) -> PaymentUpdate:
        # En fake, aceptamos querystring para simular el resultado
        paid = request.GET.get("paid") == "1"
        provider_session_id = request.GET.get("psid", "") or "fake-session"
        status = "PAID" if paid else "FAILED"
        return PaymentUpdate(
            provider_session_id=provider_session_id,
            status=status,
            raw={"query": request.GET.dict()},
        )

    def refund(self, intent, amount: int | None = None) -> bool:
        # Simulación: siempre "éxito"
        return True
