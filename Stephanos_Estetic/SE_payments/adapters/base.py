# SE_payments/adapters/base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
from django.http import HttpRequest

@dataclass
class PaymentInitResult:
    """Resultado al iniciar un checkout en el proveedor."""
    redirect_url: str
    provider_session_id: Optional[str] = None  # e.g. token/orden del gateway

@dataclass
class PaymentUpdate:
    """Resultado de procesar un webhook/retorno del proveedor."""
    provider_session_id: str
    status: str               # "PAID", "FAILED", "PENDING", etc.
    raw: Any                  # payload crudo para auditoría

class PaymentProvider(ABC):
    """Interfaz que deben implementar los proveedores de pago."""
    slug: str  # p.ej. "webpay", "flow", "mercadopago", "fake"

    def __init__(self, slug: str):
        self.slug = slug

    @abstractmethod
    def create_checkout(self, intent, request: HttpRequest) -> PaymentInitResult:
        """
        Crea la sesión de pago en el gateway para 'intent' y devuelve la URL de redirección.
        Debe actualizar intent.provider_session_id si aplica.
        """
        ...

    @abstractmethod
    def handle_webhook(self, request: HttpRequest) -> PaymentUpdate:
        """
        Procesa un webhook llamado por el gateway (o retorno firmado si el proveedor no usa webhook).
        Debe validar firma, extraer session_id y determinar status final.
        """
        ...

    @abstractmethod
    def refund(self, intent, amount: Optional[int] = None) -> bool:
        """
        Pide reembolso total o parcial (amount en CLP). Devuelve True si el proveedor lo aceptó.
        """
        ...
