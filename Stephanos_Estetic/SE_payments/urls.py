# SE_payments/urls.py
from django.urls import path
from . import views

app_name = "payments"
urlpatterns = [
    path("payments/checkout/", views.checkout_dummy, name="checkout"),
    path("payments/return/", views.payment_return, name="return"),
    path("payments/cancel/", views.payment_cancel, name="cancel"),
]
