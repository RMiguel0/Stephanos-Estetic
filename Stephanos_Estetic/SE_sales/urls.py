from django.urls import path
from . import views

app_name = 'SE_sales'

urlpatterns = [
    path('', views.sales, name='sales'),
]