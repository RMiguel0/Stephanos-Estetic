# SE_users/models.py
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import UniqueConstraint

from SE_sales.models import Order

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=255, blank=True)
    display_name = models.CharField(max_length=255, blank=True, default="")  # <- si lo quieres
    phone = models.CharField(max_length=30, blank=True)
    picture = models.URLField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # prioriza display_name si existe, luego full_name, luego username
        return self.display_name or self.full_name or self.user.get_username()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class UserOrderHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order_history")
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']
        constraints = [
            UniqueConstraint(fields=['user', 'order'], name='uix_user_order_history')
        ]
        indexes = [
            models.Index(fields=['user', 'viewed_at']),
            models.Index(fields=['order']),
        ]