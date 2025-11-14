# SE_sales/serializers.py
from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    # Campo calculado que devuelve la URL pública de la imagen
    public_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "sku",
            "slug",
            "name",
            "stock",
            "price",
            "activo",
            "public_image_url",
        ]

    def get_public_image_url(self, obj):
        """
        Prioridad:
        1) image_url (externa configurada a mano)
        2) image (archivo subido a Django)
        """
        if getattr(obj, "image_url", None):
            return obj.image_url
        image = getattr(obj, "image", None)
        if image:
            try:
                return image.url
            except Exception:
                return ""
        return ""


# ----- Checkout -----

class CheckoutItemSerializer(serializers.Serializer):
    sku = serializers.CharField()
    qty = serializers.IntegerField(min_value=1)


class CheckoutSerializer(serializers.Serializer):
    """
    Serializer genérico para el endpoint de checkout.
    Si tu api.py espera más campos (ej. teléfono, dirección),
    se los puedes agregar acá.
    """
    items = CheckoutItemSerializer(many=True)
    customer_name = serializers.CharField(
        required=False, allow_blank=True
    )
    customer_email = serializers.EmailField(
        required=False, allow_blank=True
    )
