from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.db import transaction
from django.utils.text import slugify

class Product(models.Model):
    sku   = models.CharField(max_length=32, unique=True, db_index=True, blank=True)
    name  = models.CharField(max_length=255)
    stock = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True, db_index=True)

    image = models.ImageField(upload_to="products/", blank=True, null=True)
    image_url = models.URLField(blank=True)

    slug  = models.SlugField(max_length=140, unique=True, blank=True)  # 👈 así

    def __str__(self):
        return f"{self.sku or '-'} — {self.name}"


    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name="product_price_gte_0",
            ),
        ]

    def consume_stock(self, qty: int):
        """Descuenta stock de forma segura dentro de una transacción."""
        if qty <= 0:
            return
        if self.stock < qty:
            raise ValueError(f"Stock insuficiente para {self.name}")
        self.stock = models.F("stock") - qty
        self.save(update_fields=["stock"])



class Order(models.Model):
    created_at     = models.DateTimeField(auto_now_add=True)
    customer_name  = models.CharField(max_length=255, blank=True)
    customer_email = models.EmailField(blank=True)
    total_amount   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='orders'
    )
    status = models.CharField(max_length=32, default='pending', db_index=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.pk} – {self.customer_name or 'sin nombre'}"

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["customer_email"]),
        ]

    def recompute_total(self, save=True):
        """
        Recalcula el total de la orden sumando tanto los productos como los servicios
        asociados. Si existen ServiceOrderItems relacionados (service_items),
        también se incluyen en el total.
        """
        product_total = self.items.aggregate(s=Sum("line_total"))["s"] or 0
        service_total = 0
        # Incluir el total de servicios si la relación existe
        if hasattr(self, "service_items"):
            service_total = self.service_items.aggregate(s=Sum("line_total"))["s"] or 0
        total = (product_total or 0) + (service_total or 0)
        self.total_amount = total
        if save:
            self.save(update_fields=["total_amount"])
        return total
    
    @transaction.atomic
    def mark_paid(self, user=None):
        """Marca la orden como pagada y descuenta stock (idempotente)."""
        if self.status == "paid":
            return self  # ya procesada → idempotencia

        # Descontar stock
        for item in self.items.select_related("product").select_for_update():
            item.product.consume_stock(item.qty)

        # Marcar pagada
        self.status = "paid"
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at"])

        # Registrar en historial
        if user:
            from SE_users.models import UserOrderHistory
            UserOrderHistory.objects.get_or_create(user=user, order=self)

        return self


class OrderItem(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product    = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty        = models.PositiveIntegerField()
    price_at   = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot del precio
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Item({self.product.name}) x{self.qty} en Order #{self.order_id}"

    class Meta:
        ordering = ["order_id", "id"]
        constraints = [
            models.CheckConstraint(check=models.Q(qty__gt=0), name="orderitem_qty_gt_0"),
            models.CheckConstraint(check=models.Q(price_at__gte=0), name="orderitem_price_at_gte_0"),
            models.CheckConstraint(check=models.Q(line_total__gte=0), name="orderitem_line_total_gte_0"),
        ]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product"]),
        ]

    # --- Lógica de totales ---
    def save(self, *args, **kwargs):
        if self.price_at is None:  # o: if not self.price_at
            self.price_at = self.product.price
        self.line_total = (self.qty or 0) * (self.price_at or 0)
        super().save(*args, **kwargs)
        self.order.recompute_total()
        
    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        order.recompute_total()


class ServiceOrderItem(models.Model):
    """
    Item de servicio vinculado a una Order, equivalente a OrderItem pero para servicios.
    Permite registrar el servicio reservado (u ofrecido) dentro de una orden de venta,
    conservando el precio y la cantidad al momento de la compra. No descuenta stock.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="service_items")
    service = models.ForeignKey("SE_services.Service", on_delete=models.PROTECT)
    qty = models.PositiveIntegerField()
    price_at = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot del precio
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Servicio({self.service.name}) x{self.qty} en Orden #{self.order_id}"

    class Meta:
        ordering = ["order_id", "id"]
        constraints = [
            models.CheckConstraint(check=models.Q(qty__gt=0), name="serviceorderitem_qty_gt_0"),
            models.CheckConstraint(check=models.Q(price_at__gte=0), name="serviceorderitem_price_at_gte_0"),
            models.CheckConstraint(check=models.Q(line_total__gte=0), name="serviceorderitem_line_total_gte_0"),
        ]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["service"]),
        ]

    # --- Lógica de totales ---
    def save(self, *args, **kwargs):
        if self.price_at is None:
            self.price_at = self.service.price
        self.line_total = (self.qty or 0) * (self.price_at or 0)
        super().save(*args, **kwargs)
        # actualiza total de la orden
        self.order.recompute_total()

    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        order.recompute_total()
