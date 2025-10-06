# SE_sales/forms.py
from django import forms

class InventoryUploadForm(forms.Form):
    file = forms.FileField(
        help_text="Archivo .xlsx o .csv con columnas: SKU, Stock",
        label="Archivo de inventario"
    )
