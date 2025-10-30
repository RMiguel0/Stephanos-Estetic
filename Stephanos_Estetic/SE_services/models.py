# SE_services/models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Service(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=60)
    buffer_before = models.PositiveIntegerField(default=0)
    buffer_after = models.PositiveIntegerField(default=0)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField(default=True)

    image = models.ImageField(upload_to="services/", blank=True, null=True)
    image_url = models.URLField(blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            cand = base
            i = 1
            while Service.objects.filter(slug=cand).exclude(pk=self.pk).exists():
                cand = f"{base}-{i}"
                i += 1
            self.slug = cand
        super().save(*args, **kwargs)

    @property
    def public_image_url(self) -> str:
        if self.image_url:
            return self.image_url
        if self.image:
            try:
                return self.image.url
            except Exception:
                return ""
        return ""

class AvailabilitySlot(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="slots")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=["starts_at", "service"])]

    def __str__(self):
        return f"{self.service.name} | {self.starts_at:%Y-%m-%d %H:%M}–{self.ends_at:%H:%M}"

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
