"""
Utilidades para agregar automáticamente eventos al calendario de la pyme a
través de la API de Google Calendar. Para habilitar esta funcionalidad debes
configurar las credenciales de servicio en settings y asignar permisos al
calendario.
"""
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


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

    # Si falta algo de la configuración, no hacemos nada
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
        end_dt = getattr(booking.slot, "ends_at", None) or booking.slot.starts_at

        # Construye el evento básico con título, descripción y fechas
        event = {
            "summary": f"{booking.slot.service.name} – {booking.customer_name}",
            "description": (
                f"Servicio: {booking.slot.service.name}\n"
                f"Cliente: {booking.customer_name} ({booking.customer_email})\n"
                f"Notas: {booking.notes or '-'}"
            ),
            "start": {"dateTime": start_dt.isoformat()},
            "end": {"dateTime": end_dt.isoformat()},
        }

        # Opcionalmente añade la ubicación si está configurada en settings
        location = getattr(settings, "BOOKING_LOCATION", None)
        if location:
            event["location"] = location

        # IMPORTANTE: no usamos attendees ni sendUpdates para evitar
        # el error "forbiddenForServiceAccounts" en cuentas Gmail normales
        service.events().insert(
            calendarId=cal_id,
            body=event,
            # sendUpdates="none",  # si quisieras ser explícito
        ).execute()

        return True

    except Exception as e:
        logger.exception("Google Calendar insert failed")
        print("Google Calendar insert failed:", e)
        raise
