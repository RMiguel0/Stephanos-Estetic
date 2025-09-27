from django.urls import path
from .views import services_list

app_name = 'services'
urlpatterns = [
    path('services/', services_list, name='services-list'),
]
