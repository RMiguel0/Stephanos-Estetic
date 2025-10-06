# SE_sales/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product

PREFIX = "ST-"       # elige tu prefijo
PAD = 6              # ST-000001  -> ancho 6

@receiver(post_save, sender=Product)
def set_sku_from_id(sender, instance, created, **kwargs):
    if created and not instance.sku:
        instance.sku = f"{PREFIX}{instance.id:0{PAD}d}"
        # Si quieres “0-based visual”: usa (instance.id - 1) pero ojo con id=1 -> 0
        instance.save(update_fields=["sku"])
