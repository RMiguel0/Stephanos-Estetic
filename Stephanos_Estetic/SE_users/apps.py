# SE_users/apps.py
from django.apps import AppConfig

class SeUsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "SE_users"

    def ready(self):
        import SE_users.signals  # importa las señales al arrancar
