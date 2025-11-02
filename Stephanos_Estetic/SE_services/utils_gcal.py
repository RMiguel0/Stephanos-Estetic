"""
Utilidades para agregar automáticamente eventos al calendario de la pyme a
través de la API de Google Calendar. Para habilitar esta funcionalidad debes
configurar las credenciales de servicio en settings y asignar permisos al
calendario.
"""
import os
from django.conf import settings


def insert_business_event(booking):
    """
    Inserta un evento en el calendario de la empresa representando la reserva.
    Requiere que GOOGLE_CALENDAR_SERVICE_ENABLED sea True, que
    GOOGLE_CALENDAR_CALENDAR_ID y GOOGLE_CREDENTIALS_FILE estén configurados
    y que el archivo exista. Si alguna de estas condiciones no se cumple, la
    función no hace nada y devuelve False.
    """
    enabled = getattr(settings, "GOOGLE_CALENDAR_SERVICE_ENABLED", False)
    cal_id = getattr(settings, "GOOGLE_CALENDAR_CALENDAR_ID", None)
    creds_path = getattr(settings, "GOOGLE_CREDENTIALS_FILE", None)
    if not (enabled and cal_id and creds_path and os.path.exists(creds_path)):
        return False
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        creds = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=["https://www.googleapis.com/auth/calendar"],
        )
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        # Determinar fecha de inicio y fin
        start_dt = booking.slot.starts_at
        end_dt = booking.slot.ends_at if hasattr(booking.slot, "ends_at") else booking.slot.starts_at
        event = {
            "summary": f"{booking.slot.service.name} – {booking.customer_name}",
            "description": f"Notas: {booking.notes or '-'} / Email: {booking.customer_email}",
            "start": {"dateTime": start_dt.isoformat()},
            "end": {"dateTime": end_dt.isoformat()},
        }
        service.events().insert(calendarId=cal_id, body=event, sendUpdates="none").execute()
        return True
    except Exception:
        return False