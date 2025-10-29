import uuid
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import models

class PaymentIntent(models.Model):
    class Status(models.TextChoices):
        AUTHORIZED = "AUTHORIZED"
        FAILED = "FAILED"
        ABORTED = "ABORTED"
        REVERSED = "REVERSED"
        PENDING = "PENDING"

    order = models.ForeignKey(
        "SE_sales.Order",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="payment_intents"
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buy_order = models.CharField(max_length=64, unique=True, db_index=True)
    token = models.CharField(max_length=128, db_index=True)
    session_id = models.CharField(max_length=64, blank=True, null=True)

    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)

    vci = models.CharField(max_length=8, blank=True, null=True)
    authorization_code = models.CharField(max_length=10, blank=True, null=True)
    accounting_date = models.CharField(max_length=16, blank=True, null=True)
    transaction_date = models.DateTimeField(blank=True, null=True)
    payment_type_code = models.CharField(max_length=8, blank=True, null=True)
    installments_number = models.PositiveIntegerField(default=0)
    card_last4 = models.CharField(max_length=4, blank=True, null=True)

    raw = models.JSONField(default=dict)  # respuesta completa de Transbank

    # (Opcional) referencia a tu Order real:
    # from SE_sales.models import Order
    # order = models.ForeignKey("SE_sales.Order", null=True, blank=True,
    #                           on_delete=models.SET_NULL, related_name="payments")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.buy_order} {self.status} ${self.amount}"
        