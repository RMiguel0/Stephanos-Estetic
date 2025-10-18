from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

from SE_services.models import ServiceProvider, Service, AvailabilitySlot

LOCAL_TZ = ZoneInfo("America/Santiago")

def daterange(d0: date, d1: date):
    cur = d0
    while cur <= d1:
        yield cur
        cur += timedelta(days=1)

class Command(BaseCommand):
    help = "Publica slots explícitos para un provider y servicio en un rango de fechas, en pasos de duración + buffers."

    def add_arguments(self, parser):
        parser.add_argument("--provider-id", type=int, required=True)
        parser.add_argument("--service-id", type=int, required=True)
        parser.add_argument("--date-start", type=str, required=True, help="YYYY-MM-DD")
        parser.add_argument("--date-end", type=str, required=True, help="YYYY-MM-DD")
        parser.add_argument("--start", type=str, required=True, help="HH:MM (ej. 10:00)")
        parser.add_argument("--end", type=str, required=True, help="HH:MM (ej. 18:00)")

    def handle(self, *args, **opts):
        provider_id = opts["provider_id"]
        service_id = opts["service_id"]
        date_start = datetime.strptime(opts["date_start"], "%Y-%m-%d").date()
        date_end = datetime.strptime(opts["date_end"], "%Y-%m-%d").date()
        hh_s, mm_s = map(int, opts["start"].split(":"))
        hh_e, mm_e = map(int, opts["end"].split(":"))

        try:
            provider = ServiceProvider.objects.get(id=provider_id)
            service = Service.objects.get(id=service_id, provider=provider, active=True)
        except ServiceProvider.DoesNotExist:
            raise CommandError("Provider no existe")
        except Service.DoesNotExist:
            raise CommandError("Service no existe o no pertenece al provider")

        step = service.duration_minutes + service.buffer_before + service.buffer_after
        duration = service.duration_minutes

        total_created = 0
        for day in daterange(date_start, date_end):
            start_local = datetime(day.year, day.month, day.day, hh_s, mm_s, tzinfo=LOCAL_TZ)
            end_local   = datetime(day.year, day.month, day.day, hh_e, mm_e, tzinfo=LOCAL_TZ)

            cur = start_local
            while cur + timedelta(minutes=duration) <= end_local:
                s_local = cur
                e_local = cur + timedelta(minutes=duration)

                AvailabilitySlot.objects.get_or_create(
                    provider=provider,
                    service=service,
                    starts_at=s_local.astimezone(ZoneInfo("UTC")),
                    ends_at=e_local.astimezone(ZoneInfo("UTC")),
                    defaults={"is_active": True}
                )
                total_created += 1
                cur += timedelta(minutes=step)

        self.stdout.write(self.style.SUCCESS(f"Slots creados/asegurados: {total_created}"))
