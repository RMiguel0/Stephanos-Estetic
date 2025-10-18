from django.contrib import admin
from .models import ServiceProvider, Service, AvailabilitySlot, Booking

class AvailabilitySlotInline(admin.TabularInline):
    model = AvailabilitySlot
    extra = 4  # muestra 4 filas vacías para crear rápido
    fields = ("starts_at", "ends_at", "is_active")
    ordering = ("starts_at",)

class BookingInline(admin.StackedInline):
    model = Booking
    extra = 0
    can_delete = False
    readonly_fields = ("customer_name", "customer_email", "status", "created_at")

@admin.register(ServiceProvider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("id", "display_name", "user")
    search_fields = ("display_name", "user__username")

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "provider", "duration_minutes", "price", "active")
    list_filter = ("provider", "active")
    search_fields = ("name",)
    inlines = [AvailabilitySlotInline]  # crea slots directo desde el servicio

@admin.register(AvailabilitySlot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ("id", "provider", "service", "starts_at", "ends_at", "is_active")
    list_filter = ("provider", "service", "is_active")
    search_fields = ("provider__display_name", "service__name")
    date_hierarchy = "starts_at"
    inlines = [BookingInline]  # ver la reserva asociada, si existe

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "slot", "customer_name", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("customer_name", "customer_email")
