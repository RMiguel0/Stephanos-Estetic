# SE_sales/admin.py
from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import Product, Order, OrderItem


# ---------- Product (como lo tienes) ----------
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
    list_display = ("sku", "name", "stock", "price")
    readonly_fields = ("sku",)  # ejemplo
    search_fields = ("sku", "name")


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

    list_display = ("id", "customer_name", "customer_email", "total_amount", "status", "paid_at")
    list_filter  = ("status", "paid_at")
    search_fields = ("customer_name", "customer_email", "id")

    # vuelve TODOS los campos de Order solo lectura
    def get_readonly_fields(self, request, obj=None):
        # incluye ForeignKeys y DateTime, etc.
        fields = [f.name for f in self.model._meta.fields]
        # si tu modelo tiene ManyToMany, añádelos también:
        fields += [m.name for m in self.model._meta.many_to_many]
        return fields

    # no permitir crear / borrar / editar
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # mantener la vista de detalle como read-only
    def has_change_permission(self, request, obj=None):
        # True para que se pueda “ver” el detalle en el admin,
        # pero como todos los campos son readonly, no podrán modificarlos.
        return True

    # opcional: quitar acciones masivas
    def get_actions(self, request):
        return {}
