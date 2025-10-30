# SE_services/admin.py
from django.contrib import admin
from .models import Service, AvailabilitySlot, Booking

class AvailabilitySlotInline(admin.TabularInline):
    model = AvailabilitySlot
    extra = 4
    fields = ("starts_at", "ends_at", "is_active")
    ordering = ("starts_at",)

class BookingInline(admin.StackedInline):
    model = Booking
    extra = 0
    can_delete = False
    readonly_fields = ("customer_name", "customer_email", "status", "created_at")

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "duration_minutes", "price", "active")
    list_filter = ("active",)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [AvailabilitySlotInline]

@admin.register(AvailabilitySlot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ("id", "service", "starts_at", "ends_at", "is_active")
    list_filter = ("service", "is_active")
    search_fields = ("service__name",)
    date_hierarchy = "starts_at"
    inlines = [BookingInline]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "slot", "customer_name", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("customer_name", "customer_email")
