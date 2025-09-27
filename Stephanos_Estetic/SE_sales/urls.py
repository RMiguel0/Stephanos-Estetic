from django.urls import path
from .views import sales_list

app_name = 'sales'
urlpatterns = [
    path('sales/', sales_list, name='sales-list'),
]
