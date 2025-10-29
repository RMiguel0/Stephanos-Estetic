# SE_sales/services.py
from django.db import transaction
from django.utils import timezone
from django.db.models import F
from SE_sales.models import Order
from SE_users.models import UserOrderHistory


@transaction.atomic
def finalize_paid_order(order_id: int, user):
    """
    Marca la orden como pagada, descuenta stock y registra en historial.
    Idempotente: si la orden ya está pagada, no repite operaciones.
    """
    # Bloqueo pesimista (evita race conditions en stock)
    order = Order.objects.select_for_update().get(pk=order_id)

    # Si ya está procesada, no duplicar
    if order.status == "paid":
        if user:
            UserOrderHistory.objects.get_or_create(user=user, order=order)
        return order

    # Consumir stock
    items = order.items.select_related("product").select_for_update()
    for it in items:
        if it.product.stock < it.qty:
            raise ValueError(f"Stock insuficiente para {it.product.name}")
        it.product.stock = F("stock") - it.qty
        it.product.save(update_fields=["stock"])

    # Marcar como pagada
    order.status = "paid"
    order.paid_at = timezone.now()
    order.save(update_fields=["status", "paid_at"])

    # Registrar historial del usuario
    if user:
        UserOrderHistory.objects.get_or_create(user=user, order=order)

    return order
