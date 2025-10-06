from django.db import models

class Product(models.Model):
    sku   = models.CharField(max_length=32, unique=True, db_index=True, blank=True)
    name  = models.CharField(max_length=255)
    stock = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.sku} - {self.name}"

class Order(models.Model):
    created_at    = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(max_length=255, blank=True)
    customer_email= models.EmailField(blank=True)
    total_amount  = models.DecimalField(max_digits=12, decimal_places=2, default=0)

class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product  = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty      = models.PositiveIntegerField()
    price_at = models.DecimalField(max_digits=10, decimal_places=2)  # precio snapshot
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
