# SE_payments/urls.py
from django.urls import path
from .views import webpay_create, webpay_commit, checkout_dummy, payment_return, payment_cancel

app_name = "payments"
urlpatterns = [
    path("checkout/", checkout_dummy, name="checkout"),
    path("return/", payment_return, name="return"),
    path("cancel/", payment_cancel, name="cancel"),
    
    path("create", webpay_create, name="webpay_create"),
    path("commit", webpay_commit, name="webpay_commit"),
]
