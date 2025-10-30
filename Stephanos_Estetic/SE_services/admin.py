# SE_services/admin.py
from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from django.utils.text import slugify
from .models import Service, AvailabilitySlot, Booking


# --------- Import/Export para Service ----------
class ServiceResource(resources.ModelResource):
    name = fields.Field(attribute="name", column_name="name")
    slug = fields.Field(attribute="slug", column_name="slug")
    description = fields.Field(attribute="description", column_name="description")
    duration_minutes = fields.Field(attribute="duration_minutes", column_name="duration_minutes")
    price = fields.Field(attribute="price", column_name="price")
    active = fields.Field(attribute="active", column_name="active")

    class Meta:
        model = Service
        import_id_fields = ("slug",)
        fields = ("name", "slug", "description", "duration_minutes", "price", "active")
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        if not row.get("slug") and row.get("name"):
            row["slug"] = slugify(row["name"])


# --------- Inlines ----------
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


# --------- Admins ----------
@admin.register(Service)
class ServiceAdmin(ImportExportModelAdmin):  # hereda solo esto, no readonly
    resource_class = ServiceResource
    list_display = ("id", "name", "slug", "duration_minutes", "price", "active")
    list_filter = ("active",)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [AvailabilitySlotInline]
    save_on_top = True
    list_per_page = 50
    ordering = ("name",)

    # 🔓 Asegura que nada esté readonly
    readonly_fields = ()

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


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
