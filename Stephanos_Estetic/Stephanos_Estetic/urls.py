"""
URL configuration for Stephanos_Estetic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('SE_donations/', include(('SE_donations.urls', 'SE_donations'), namespace='SE_donations')),
    path('SE_sales/',     include(('SE_sales.urls',     'SE_sales'),     namespace='SE_sales')),
    path('SE_services/',  include(('SE_services.urls',  'SE_services'),  namespace='SE_services')),

    path('', lambda request: render(request, 'home.html'), name='home'),
]