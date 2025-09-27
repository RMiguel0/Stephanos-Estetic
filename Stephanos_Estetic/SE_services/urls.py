from django.urls import path
from . import views

app_name = 'SE_services'

urlpatterns = [
    path('', views.services, name='services'),
]