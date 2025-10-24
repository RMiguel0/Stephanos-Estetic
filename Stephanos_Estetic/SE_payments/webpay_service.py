# SE_payments/webpay_service.py
from django.conf import settings
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys

def _options() -> WebpayOptions:
    # Usa credenciales de integración en TEST
    env = getattr(settings, "WEBPAY_ENV", "TEST").upper()
    if env == "TEST":
        return WebpayOptions(
            commerce_code=IntegrationCommerceCodes.WEBPAY_PLUS,
            api_key=IntegrationApiKeys.WEBPAY,
            integration_type=IntegrationType.TEST,
        )
    # En LIVE usa tus credenciales reales
    return WebpayOptions(
        commerce_code=settings.WEBPAY_COMMERCE_CODE,
        api_key=settings.WEBPAY_API_KEY,
        integration_type=IntegrationType.LIVE,
    )

def create_tx(buy_order: str, session_id: str, amount: int, return_url: str):
    tx = Transaction(options=_options())
    return tx.create(
        buy_order=buy_order,
        session_id=session_id,
        amount=int(amount),
        return_url=return_url,
    )

def commit_tx(token_ws: str):
    tx = Transaction(options=_options())
    return tx.commit(token_ws)
