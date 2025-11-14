from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html  # 👈 para la miniatura
from .models import Product, Order, OrderItem


# ---------- Product (import/export) ----------
class ProductResource(resources.ModelResource):
    sku   = fields.Field(attribute="sku", column_name="SKU")
    stock = fields.Field(attribute="stock", column_name="Stock")

    class Meta:
        model = Product
        import_id_fields = ("sku",)
        fields = ("sku", "stock")
        skip_unchanged = True
        report_skipped = True


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource

    # mostramos imagen, activo y slug
    list_display = ("sku", "name", "stock", "price", "activo", "slug", "image_thumb")
    search_fields = ("sku", "name", "slug")
    list_filter = ("activo",)

    # sku no editable, image_thumb solo lectura
    readonly_fields = ("sku", "image_thumb")

    # que el slug se propague desde name en el admin
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        ("Datos básicos", {
            "fields": ("sku", "name", "slug", "price", "stock", "activo"),
        }),
        ("Imagen", {
            "fields": ("image", "image_url", "image_thumb"),
        }),
    )

    def image_thumb(self, obj):
        """
        Miniatura de la imagen del producto (usa image_url si existe, 
        si no, image.file).
        """
        url = ""
        if getattr(obj, "image_url", ""):
            url = obj.image_url
        elif getattr(obj, "image", None):
            try:
                url = obj.image.url
            except Exception:
                url = ""

        if not url:
            return "(sin imagen)"

        return format_html(
            '<img src="{}" style="max-height:80px; max-width:80px; border-radius:4px;" />',
            url,
        )

    image_thumb.short_description = "Vista previa"


# ---------- Order / OrderItem como histórico ----------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    # todos los campos del item en solo lectura
    readonly_fields = [f.name for f in OrderItem._meta.fields]

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        # evita edición inline
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

    list_display = ("id", "customer_name", "customer_email",
                    "total_amount", "status", "paid_at")
    list_filter  = ("status", "paid_at")
    search_fields = ("customer_name", "customer_email", "id")

    # vuelve TODOS los campos de Order solo lectura
    def get_readonly_fields(self, request, obj=None):
        fields = [f.name for f in self.model._meta.fields]
        fields += [m.name for m in self.model._meta.many_to_many]
        return fields

    # no permitir crear / borrar / editar
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # mantener la vista de detalle como read-only
    def has_change_permission(self, request, obj=None):
        return True

    # opcional: quitar acciones masivas
    def get_actions(self, request):
        return {}
