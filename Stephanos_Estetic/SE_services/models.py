from django.db import models
from django.conf import settings
from django.db import models
from django.utils import timezone

class ServiceProvider(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=120)

    def __str__(self): 
        return self.display_name

class Service(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=60)
    buffer_before = models.PositiveIntegerField(default=0)  # min
    buffer_after = models.PositiveIntegerField(default=0)   # min
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="services")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField(default=True)

    def __str__(self): 
        return self.name

class AvailabilitySlot(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="slots")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="slots")
    starts_at = models.DateTimeField()  # aware
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("provider", "starts_at")]
        indexes = [models.Index(fields=["provider", "starts_at"])]

    def __str__(self): 
        return f"{self.provider} | {self.starts_at:%Y-%m-%d %H:%M}–{self.ends_at:%H:%M}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("paid", "Pagada"),
        ("cancelled", "Cancelada"),
        ("fulfilled", "Completada"),
        ("no_show", "No se presentó"),
    ]
    slot = models.OneToOneField(AvailabilitySlot, on_delete=models.PROTECT, related_name="booking")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="bookings")
    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return f"Reserva {self.id} {self.slot.starts_at:%Y-%m-%d %H:%M} ({self.status})"

