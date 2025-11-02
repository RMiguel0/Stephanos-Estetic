# views.py
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from django.db import transaction
from zoneinfo import ZoneInfo
import zoneinfo
from datetime import datetime, timedelta
import json, re
from django.utils.text import slugify

from .models import Service, AvailabilitySlot, Booking
from django.conf import settings
from django.shortcuts import redirect
from SE_payments.webpay_service import create_tx, commit_tx
from .utils_email import send_booking_emails
from .utils_gcal import insert_business_event
from django.contrib.auth import get_user_model

LOCAL_TZ = ZoneInfo("America/Santiago")
UTC_TZ = ZoneInfo("UTC")

def _jerror(msg, status=400):
    return JsonResponse({"error": msg}, status=status)

# -------- helpers ----------
def _parse_bool(v, default=False):
    if v is None: return default
    return str(v).lower() in ("1","true","t","yes","y")

def _parse_date(s):
    y,m,d = map(int, s.split("-"))
    return datetime(y,m,d,0,0,0,tzinfo=LOCAL_TZ)

def _service_pk_from_any(service_id: str) -> int | None:
    if service_id is None: return None
    service_id = str(service_id)
    if service_id.isdigit():
        return int(service_id)
    m = re.fullmatch(r"svc(\d+)", service_id, flags=re.I)
    if m: return int(m.group(1))
    s = Service.objects.filter(name__iexact=service_id).first()
    return s.id if s else None

def _serialize_service(s: Service):
    return {
        "id": s.id,
        "name": s.name,
        "slug": s.slug,                 # ← ahora viene del modelo
        "description": s.description,
        "duration_minutes": s.duration_minutes,
        "price": float(s.price),
        "active": s.active,
        "ext_id": f"svc{s.id}",         # si tu front usa 'svcX', lo mantenemos
        # ya no incluimos provider_id
    }




# -------- endpoints ----------
@ensure_csrf_cookie
def csrf_ok(request):
    return JsonResponse({"detail": "ok"})

@require_GET
def services_list(request):
    """
    GET /api/services/?active=true
    Devuelve ARRAY plano para calzar con tu Services.jsx
    """
    active = _parse_bool(request.GET.get("active"), default=True)

    qs = Service.objects.all()
    if active:
        qs = qs.filter(active=True)

    qs = qs.order_by("name")
    data = [_serialize_service(s) for s in qs]
    return JsonResponse(data, safe=False)



@require_GET
def service_schedules(request):
    """
    GET /api/service_schedules/?service_id=svc1&is_booked=false&date_from=YYYY-MM-DD[&date_to=YYYY-MM-DD]
    Devuelve ARRAY plano con los slots (compat con front).
    """
    service_id_raw = request.GET.get("service_id")
    if not service_id_raw:
        return HttpResponseBadRequest("service_id es obligatorio")
    service_pk = _service_pk_from_any(service_id_raw)
    if not service_pk:
        return HttpResponseBadRequest("service_id no encontrado")

    is_booked = _parse_bool(request.GET.get("is_booked"), default=False)
    date_from = request.GET.get("date_from")
    if not date_from:
        return HttpResponseBadRequest("date_from (YYYY-MM-DD) es obligatorio")
    start_local = _parse_date(date_from)

    date_to = request.GET.get("date_to")
    if date_to:
        end_local = _parse_date(date_to) + timedelta(days=1) - timedelta(seconds=1)
    else:
        end_local = start_local + timedelta(hours=23, minutes=59, seconds=59)

    # ← SIN provider_id
    filters = {
        "service_id": service_pk,
        "is_active": True,
        "starts_at__gte": start_local.astimezone(UTC_TZ),
        "starts_at__lte": end_local.astimezone(UTC_TZ),
    }

    qs = (AvailabilitySlot.objects
          .filter(**filters)
          .select_related("service")     # ← solo service
          .order_by("starts_at"))

    items = []
    for slot in qs:
        booked = hasattr(slot, "booking")
        if is_booked != booked:
            continue
        items.append({
            "id": slot.id,  # service_schedule_id
            "service_id": service_id_raw,
            "starts_at": slot.starts_at.astimezone(LOCAL_TZ).isoformat(),
            "ends_at": slot.ends_at.astimezone(LOCAL_TZ).isoformat(),
            "is_booked": booked,
            **({"booking_id": slot.booking.id, "booking_status": slot.booking.status} if booked else {})
        })

    return JsonResponse(items, safe=False)


@csrf_exempt
def create_booking(request):
    """
    POST /api/bookings/
    body JSON:
      { "service_schedule_id": <int>  // o "slot_id"
        "customer_name": "...",        // requerido solo si NO hay sesión
        "customer_email": "...",       // requerido solo si NO hay sesión
        "customer_phone": "...",       // opcional
        "notes": "..." }               // opcional
    """
    # 1) Content-Type y carga JSON
    ctype = (request.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    if ctype != "application/json":
        return _jerror("Content-Type debe ser application/json", status=415)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return _jerror("JSON inválido")

    # 2) Params básicos
    slot_id = payload.get("slot_id") or payload.get("service_schedule_id")
    if not slot_id:
        return _jerror("slot_id o service_schedule_id es obligatorio")

    try:
        slot_id = int(slot_id)
    except (ValueError, TypeError):
        return _jerror("slot_id inválido")

    notes = (payload.get("notes") or "").strip()
    user = request.user if request.user.is_authenticated else None

    # 3) Transacción + bloqueo (evita doble click)
    try:
        with transaction.atomic():
            slot = (
                AvailabilitySlot.objects
                .select_for_update()
                .select_related("service")
                .get(id=slot_id, is_active=True)
            )

            # Doble reserva
            if hasattr(slot, "booking"):
                return _jerror("El horario ya fue tomado.", status=409)

            # No permitir horarios pasados (según TZ local)
            if slot.starts_at.astimezone(LOCAL_TZ) <= timezone.now().astimezone(LOCAL_TZ):
                return _jerror("No puedes reservar un horario pasado.")

            # 4) Datos del cliente según sesión
            if user and user.is_authenticated:
                profile = getattr(user, "profile", None)
                customer_name = (
                    (getattr(profile, "full_name", "") or "").strip()
                    or f"{user.first_name} {user.last_name}".strip()
                    or user.get_username()
                )
                customer_email = user.email
                customer_phone = (getattr(profile, "phone", "") or "").strip()
            else:
                customer_name  = (payload.get("customer_name")  or "").strip()
                customer_email = (payload.get("customer_email") or "").strip()
                customer_phone = (payload.get("customer_phone") or "").strip()
                if not customer_name or not customer_email:
                    return _jerror("customer_name y customer_email son obligatorios")

            # 5) Precio y abono (20 %)
            service_price = int(slot.service.price or 0)
            try:
                deposit_amount = int(round(float(service_price) * 0.20))
            except Exception:
                deposit_amount = 0

            booking_kwargs = dict(
                slot=slot,
                customer=user if (user and user.is_authenticated) else None,
                customer_name=customer_name,
                customer_email=customer_email,
                notes=notes,
                status="pending",              # o "PENDING_PAYMENT"
                service_price=service_price,   # snapshot
                deposit_amount=deposit_amount,
                paid_amount=0,
                payment_status="PENDING",
            )
            if hasattr(Booking, "customer_phone"):
                booking_kwargs["customer_phone"] = customer_phone

            booking = Booking.objects.create(**booking_kwargs)

            # 6) Iniciar Webpay para el abono
            buy_order = f"B{booking.id}"
            session_id = str(user.id if (user and user.is_authenticated) else 0)
            site_url = (getattr(settings, "SITE_URL", "") or "").rstrip("/")
            return_url = f"{site_url}/api/bookings/commit/"

            try:
                tx_resp = create_tx(
                    buy_order=buy_order,
                    session_id=session_id,
                    amount=deposit_amount,
                    return_url=return_url,
                )
                token = tx_resp.get("token")
                url = tx_resp.get("url")
                if token:
                    booking.payment_token = token
                    booking.save(update_fields=["payment_token"])
                redirect_url = f"{url}?token_ws={token}" if (token and url) else None
            except Exception as e:
                booking.delete()
                return _jerror(f"No se pudo iniciar el pago: {str(e)}", status=500)

    except AvailabilitySlot.DoesNotExist:
        return _jerror("El slot no existe o no está activo.", status=404)

    # 7) Respuesta (con fallback de ends_at)
    ends = getattr(slot, "ends_at", None)
    if ends is None:
        from datetime import timedelta
        minutes = getattr(slot.service, "duration_minutes", 60) or 60
        ends = slot.starts_at + timedelta(minutes=minutes)

    return JsonResponse(
        {
            "booking_id": booking.id,
            "slot_id": slot.id,
            "service_id": slot.service_id,
            "service_name": slot.service.name,
            "starts_at": slot.starts_at.astimezone(LOCAL_TZ).isoformat(),
            "ends_at": ends.astimezone(LOCAL_TZ).isoformat(),
            "status": booking.status,
            "redirect_url": redirect_url,
        },
        status=201,
    )


@csrf_exempt
def booking_commit(request):
    """
    GET/POST /api/bookings/commit/?token_ws=...
    Confirma la transacción Webpay, marca booking, envía correos y redirige al FE.
    """
    token = request.GET.get("token_ws") or request.POST.get("token_ws")
    if not token:
        return _jerror("token_ws faltante", status=400)

    try:
        resp = commit_tx(token)  # tu helper de SE_payments.webpay_service
    except Exception as e:
        return _jerror(f"Error al confirmar pago: {e}", status=500)

    try:
        booking = Booking.objects.select_related("slot__service").get(payment_token=token)
    except Booking.DoesNotExist:
        return _jerror("Reserva no encontrada para token.", status=404)

    ok = str(resp.get("response_code")) == "0"

    if ok:
        booking.payment_status = "AUTHORIZED"
        booking.paid_amount = resp.get("amount", booking.deposit_amount)
        booking.status = "confirmed"
        booking.save(update_fields=["payment_status", "paid_amount", "status"])

        # marca el slot como tomado
        if not hasattr(booking.slot, "booking"):
            # Si tu modelo crea relación inversa automáticamente, omite esto
            pass

        # correos + calendar
        try:
            send_booking_emails(booking)
        except Exception as e:
            # registra/log si quieres
            pass
        try:
            insert_business_event(booking)  # si lo habilitaste
        except Exception:
            pass
    else:
        booking.payment_status = "FAILED"
        booking.status = "canceled"
        booking.save(update_fields=["payment_status", "status"])

    # Redirigir al FE con info para renderizar.
    FRONTEND_URL = getattr(settings, "FRONTEND_URL", "http://localhost:5173").rstrip("/")
    starts_local = booking.slot.starts_at.astimezone(LOCAL_TZ).strftime("%Y-%m-%dT%H:%M")
    service_name = booking.slot.service.name

    return redirect(
        f"{FRONTEND_URL}/services/booking-success"
        f"?ok={str(ok).lower()}&booking_id={booking.id}"
        f"&service={service_name}&starts_at={starts_local}"
        f"&amount={booking.deposit_amount}"
    )

