# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from django.db import transaction
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import json, re


from .models import Service, AvailabilitySlot, Booking

LOCAL_TZ = ZoneInfo("America/Santiago")
UTC_TZ = ZoneInfo("UTC")

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
        "duration_minutes": s.duration_minutes,
        "price": float(s.price),  # suele ser más cómodo en el front
        "provider_id": s.provider_id,
        "active": s.active,
        "ext_id": f"svc{s.id}",   # si tu front usa 'svcX'
    }
def _jerror(msg, status=400):
    return JsonResponse({"error": msg}, status=status)


# -------- endpoints ----------
@ensure_csrf_cookie
def csrf_ok(request):
    return JsonResponse({"detail": "ok"})

@require_GET
def services_list(request):
    """
    GET /api/services/?active=true&provider_id=1
    Devuelve **ARRAY plano** para calzar con tu Services.jsx
    """
    active = _parse_bool(request.GET.get("active"), default=True)
    provider_id = request.GET.get("provider_id")

    qs = Service.objects.all()
    if active:
        qs = qs.filter(active=True)
    if provider_id:
        try:
            qs = qs.filter(provider_id=int(provider_id))
        except ValueError:
            return HttpResponseBadRequest("provider_id inválido")

    qs = qs.order_by("name")
    data = [_serialize_service(s) for s in qs]
    # ARRAY plano, NO {"services": ...}
    return JsonResponse(data, safe=False)

@require_GET
def service_schedules(request):
    """
    GET /api/service_schedules/?service_id=svc1&is_booked=false&date_from=YYYY-MM-DD[&date_to=YYYY-MM-DD][&provider_id=1]
    Devuelve **ARRAY plano** con los slots (compat con front).
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

    provider_id = request.GET.get("provider_id")
    filters = {
        "service_id": service_pk,
        "is_active": True,
        "starts_at__gte": start_local.astimezone(UTC_TZ),
        "starts_at__lte": end_local.astimezone(UTC_TZ),
    }
    if provider_id:
        try:
            filters["provider_id"] = int(provider_id)
        except ValueError:
            return HttpResponseBadRequest("provider_id inválido")

    qs = (AvailabilitySlot.objects
          .filter(**filters)
          .select_related("service", "provider")
          .order_by("starts_at"))

    items = []
    for slot in qs:
        booked = hasattr(slot, "booking")
        if is_booked != booked:
            continue
        items.append({
            "id": slot.id,  # service_schedule_id
            "service_id": service_id_raw,
            "provider_id": slot.provider_id,
            "starts_at": slot.starts_at.astimezone(LOCAL_TZ).isoformat(),
            "ends_at": slot.ends_at.astimezone(LOCAL_TZ).isoformat(),
            "is_booked": booked,
            **({"booking_id": slot.booking.id, "booking_status": slot.booking.status} if booked else {})
        })

    # ARRAY plano, NO {"items": ...}
    return JsonResponse(items, safe=False)

def create_booking(request):
    """
    POST /api/bookings/
    body JSON:
      { "service_schedule_id": <int>  // o "slot_id"
        "customer_name": "...",
        "customer_email": "...",
        "customer_phone": "...",       // opcional (si existe en el modelo)
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

    customer_name  = (payload.get("customer_name")  or "").strip()
    customer_email = (payload.get("customer_email") or "").strip()
    customer_phone = (payload.get("customer_phone") or "").strip()  # opcional
    notes          = (payload.get("notes")          or "").strip()

    if not customer_name or not customer_email:
        return _jerror("customer_name y customer_email son obligatorios")

    user = request.user if request.user.is_authenticated else None

    # 3) Transacción + bloque de fila (anti doble-click)
    from .models import AvailabilitySlot, Booking  # importa aquí para evitar ciclos

    try:
        with transaction.atomic():
            slot = (AvailabilitySlot.objects
                    .select_for_update()
                    .select_related("service", "provider")
                    .get(id=slot_id, is_active=True))
            # doble reserva
            if hasattr(slot, "booking"):
                return _jerror("El horario ya fue tomado.", status=409)

            # pasado (según zona local)
            now_local = timezone.now().astimezone(LOCAL_TZ)
            if slot.starts_at.astimezone(LOCAL_TZ) <= now_local:
                return _jerror("No puedes reservar un horario pasado.")

            # armar kwargs, guardando phone solo si el modelo lo tiene
            booking_kwargs = dict(
                slot=slot,
                customer=user,
                customer_name=customer_name,
                customer_email=customer_email,
                notes=notes,
                status="pending",
            )
            if hasattr(Booking, "customer_phone"):
                booking_kwargs["customer_phone"] = customer_phone

            booking = Booking.objects.create(**booking_kwargs)

    except AvailabilitySlot.DoesNotExist:
        return _jerror("El slot no existe o no está activo.", status=404)

    # 4) Respuesta útil para el front
    return JsonResponse({
        "booking_id": booking.id,
        "slot_id": slot.id,
        "service_id": slot.service_id,
        "service_name": slot.service.name,
        "provider_id": slot.provider_id,
        "provider_name": slot.provider.display_name,
        "starts_at": slot.starts_at.astimezone(LOCAL_TZ).isoformat(),
        "ends_at":   slot.ends_at.astimezone(LOCAL_TZ).isoformat(),
        "status": booking.status,
    }, status=201)