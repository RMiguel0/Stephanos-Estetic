# SE_sales/urls.py
from django.urls import path
from .api import ProductListAPI, CheckoutAPI

urlpatterns = [
    path("products/", ProductListAPI.as_view(), name="products_list"),
    path("checkout/", CheckoutAPI.as_view(), name="checkout"),
]
