from django.urls import path
from .views import ContactRequestView

app_name = "contact"
urlpatterns = [
    path('contact/requests/', ContactRequestView.as_view(), name='contact-request'),
]
