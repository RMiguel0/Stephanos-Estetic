from django.urls import path
from .views import donations_list

app_name = 'donations'
urlpatterns = [
    path('donations/', donations_list, name='donations-list'),
]
