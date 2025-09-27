import uuid
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class PaymentIntent(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        REQUIRES_ACTION = "REQUIRES_ACTION"
        PAID = "PAID"
        FAILED = "FAILED"
        REFUNDED = "REFUNDED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.BigIntegerField()             # CLP en pesos (sin decimales)
    currency = models.CharField(max_length=10, default="CLP")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    description = models.CharField(max_length=140)

    # vínculo polimórfico al objeto de negocio (Order, Booking, Donation)
    ref_content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    ref_object_id = models.PositiveIntegerField()
    ref_object = GenericForeignKey('ref_content_type', 'ref_object_id')

    provider = models.CharField(max_length=30)           # "webpay", "mercadopago", etc.
    provider_session_id = models.CharField(max_length=120, blank=True)
    return_url = models.URLField()
    cancel_url = models.URLField()
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
