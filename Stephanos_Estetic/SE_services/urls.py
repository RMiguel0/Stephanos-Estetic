from django.urls import path
from .views import csrf_ok, services_list, service_schedules, create_booking

app_name = "services"

urlpatterns = [
    path("csrf/", csrf_ok, name="csrf_ok"),
    path("services/", services_list, name="services_list"),
    path("service_schedules/", service_schedules, name="service_schedules"),
    path("bookings/", create_booking, name="create_booking"),
]
