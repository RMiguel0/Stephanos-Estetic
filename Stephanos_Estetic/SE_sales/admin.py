# SE_sales/admin.py
from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import Product, Order, OrderItem  

admin.site.register(Order)      
admin.site.register(OrderItem)  


class ProductResource(resources.ModelResource):
    sku   = fields.Field(attribute="sku", column_name="SKU")
    stock = fields.Field(attribute="stock", column_name="Stock")
    # si quieres también precio:
    # price = fields.Field(attribute="price", column_name="Precio")

    class Meta:
        model = Product
        import_id_fields = ("sku",)       # actualizar por SKU
        fields = ("sku", "stock")         # columnas permitidas en import
        skip_unchanged = True
        report_skipped = True

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ("sku", "name", "stock", "price")
    readonly_fields = ("sku",)            # que no lo editen a mano
    search_fields = ("sku", "name")
