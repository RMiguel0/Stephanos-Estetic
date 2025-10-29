from django.conf import settings
from django.db import models
from django.db.models import Sum


class Product(models.Model):
    sku   = models.CharField(max_length=32, unique=True, db_index=True, blank=True)
    name  = models.CharField(max_length=255)
    stock = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        # Lo que verás en admin/listas
        return f"{self.sku or '-'} — {self.name}"

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(check=models.Q(price__gte=0), name="product_price_gte_0"),
        ]


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

    def __str__(self):
        return f"Order #{self.pk} – {self.customer_name or 'sin nombre'}"

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["customer_email"]),
        ]

    def recompute_total(self, save=True):
        total = self.items.aggregate(s=Sum("line_total"))["s"] or 0
        self.total_amount = total
        if save:
            self.save(update_fields=["total_amount"])
        return total


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
