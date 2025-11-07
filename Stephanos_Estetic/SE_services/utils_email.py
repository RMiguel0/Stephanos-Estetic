from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from datetime import datetime, timedelta, timezone as dt_timezone
from email.mime.base import MIMEBase
from email import encoders
import uuid
import zoneinfo

from .models import Booking

# Valores de configuración para correos y calendarios
SITE_NAME = getattr(settings, "SITE_NAME", "Stephanos Estetic")
SITE_URL = getattr(settings, "SITE_URL", "")
BOOKING_LOCATION = getattr(settings, "BOOKING_LOCATION", "")
PYME_NOTIFY_EMAIL = getattr(settings, "BOOKINGS_NOTIFY_EMAIL", None)

LOCAL_TZ = zoneinfo.ZoneInfo(getattr(settings, "TIME_ZONE", "UTC"))

def _ensure_aware(dt):
    """Asegura que el datetime sea aware en la zona local configurada."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # vuelve aware en tz local si vino naive
        return dt.replace(tzinfo=LOCAL_TZ)
    return dt

def _format_dt(dt):
    """
    Formatea un datetime a la forma requerida por iCalendar (UTC, YYYYMMDDTHHMMSSZ).
    Compatible con Django 5 (sin timezone.utc de Django).
    """
    if not dt:
        return ""
    dt = _ensure_aware(dt)
    dt_utc = dt.astimezone(dt_timezone.utc)
    return dt_utc.strftime("%Y%m%dT%H%M%SZ")

def build_ics(booking: Booking) -> str:
    """
    Genera un archivo .ics para la reserva usando hora de inicio y fin.
    Si no existe ends_at, calcula fin sumando duration_minutes del servicio (default 60).
    """
    uid = f"{uuid.uuid4()}@{SITE_NAME.replace(' ', '')}"

    start = _ensure_aware(getattr(booking.slot, "starts_at", None))
    # fin: usa slot.ends_at si existe; si no, suma duración del servicio
    end = getattr(booking.slot, "ends_at", None)
    end = _ensure_aware(end)
    if not end:
        minutes = getattr(booking.slot.service, "duration_minutes", 60) or 60
        end = (start or datetime.now(tz=LOCAL_TZ)) + timedelta(minutes=minutes)

    dtstart = _format_dt(start)
    dtend = _format_dt(end)

    summary = f"{SITE_NAME} – {booking.slot.service.name}"
    description = f"Reserva confirmada para {booking.customer_name}. Notas: {booking.notes or '-'}"
    location = BOOKING_LOCATION or SITE_NAME
    now = datetime.now(tz=LOCAL_TZ).astimezone(dt_timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    ics = (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        f"PRODID:-//{SITE_NAME}//Booking//ES\n"
        "CALSCALE:GREGORIAN\n"
        "METHOD:REQUEST\n"
        "BEGIN:VEVENT\n"
        f"UID:{uid}\n"
        f"DTSTAMP:{now}\n"
        f"DTSTART:{dtstart}\n"
        f"DTEND:{dtend}\n"
        f"SUMMARY:{summary}\n"
        f"DESCRIPTION:{description}\n"
        f"LOCATION:{location}\n"
        "END:VEVENT\n"
        "END:VCALENDAR\n"
    )
    return ics

def _attach_ics(message: EmailMultiAlternatives, ics_text: str, filename: str = "reserva.ics"):
    """Adjunta el contenido iCalendar como attachment."""
    part = MIMEBase("text", "calendar", **{"method": "REQUEST", "name": filename})
    part.set_payload(ics_text)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    part.add_header("Content-Class", "urn:content-classes:calendarmessage")
    message.attach(part)

def _fmt_local(dt):
    """Formatea en zona local de forma segura."""
    dt = _ensure_aware(dt)
    return dt.astimezone(LOCAL_TZ).strftime("%d-%m-%Y %H:%M")

def send_booking_emails(booking: Booking):
    """
    Envía correo de confirmación al cliente y notifica a la pyme. Adjunta .ics.
    """
    if not booking or not booking.customer_email:
        return

    # Correo al cliente
    subject_client = f"[{SITE_NAME}] Reserva confirmada"
    html_client = (
        f"<p>Hola {booking.customer_name},</p>"
        f"<p>Tu reserva de <strong>{booking.slot.service.name}</strong> está confirmada para "
        f"<strong>{_fmt_local(booking.slot.starts_at)}</strong>.</p>"
        f"<p>Notas: {booking.notes or '-'}</p>"
        f"<p>Puedes visitar nuestro sitio en <a href=\"{SITE_URL}\">{SITE_URL}</a></p>"
    )
    msg_client = EmailMultiAlternatives(
        subject_client,
        strip_tags(html_client),
        settings.DEFAULT_FROM_EMAIL,
        [booking.customer_email],
        # opcional: bcc a la pyme:
        # bcc=[PYME_NOTIFY_EMAIL] if PYME_NOTIFY_EMAIL else None,
    )
    msg_client.attach_alternative(html_client, "text/html")
    _attach_ics(msg_client, build_ics(booking))
    msg_client.send(fail_silently=False)

    # Correo a la pyme
    if PYME_NOTIFY_EMAIL:
        subject_py = f"[{SITE_NAME}] Nueva reserva"
        html_py = (
            f"<p>Se ha tomado una nueva reserva.</p>"
            f"<ul>"
            f"<li>Servicio: <strong>{booking.slot.service.name}</strong></li>"
            f"<li>Cliente: {booking.customer_name} ({booking.customer_email})</li>"
            f"<li>Teléfono: {getattr(booking, 'customer_phone', '') or '-'}</li>"
            f"<li>Fecha/Hora: {_fmt_local(booking.slot.starts_at)}</li>"
            f"<li>Abono: ${getattr(booking, 'deposit_amount', 0):,} CLP</li>"
            f"</ul>"
        )
        msg_py = EmailMultiAlternatives(
            subject_py,
            strip_tags(html_py),
            settings.DEFAULT_FROM_EMAIL,
            [PYME_NOTIFY_EMAIL],
        )
        msg_py.attach_alternative(html_py, "text/html")
        _attach_ics(msg_py, build_ics(booking), filename="reserva_pyme.ics")
        msg_py.send(fail_silently=False)
