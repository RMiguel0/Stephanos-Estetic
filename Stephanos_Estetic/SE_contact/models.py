from django.db import models

class ContactRequest(models.Model):
    name = models.CharField(max_length=80)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    # util para auditoría
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    is_handled = models.BooleanField(default=False)  # marcado por admin

    def __str__(self):
        return f"{self.name} <{self.email}> ({self.created_at:%Y-%m-%d})"
