# SE_sales/serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("sku", "name", "price", "stock")

class CheckoutItemSerializer(serializers.Serializer):
    sku = serializers.CharField()
    qty = serializers.IntegerField(min_value=1)

class CheckoutSerializer(serializers.Serializer):
    items = CheckoutItemSerializer(many=True)
    customer_name  = serializers.CharField(required=False, allow_blank=True)
    customer_email = serializers.EmailField(required=False, allow_blank=True)
