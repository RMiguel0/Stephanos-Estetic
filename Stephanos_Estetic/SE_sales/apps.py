# SE_sales/apps.py
from django.apps import AppConfig

class SeSalesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "SE_sales"

    def ready(self):
        from . import signals  # noqa
