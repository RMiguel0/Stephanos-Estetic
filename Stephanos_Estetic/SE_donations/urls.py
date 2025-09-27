from django.urls import path
from . import views

app_name = 'SE_donations'

urlpatterns = [
    path('', views.donations, name='donations'),
]