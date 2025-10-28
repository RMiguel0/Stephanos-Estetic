from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),  # login/logout/password
    path('api/', include('Stephanos_Estetic.api_urls')),
]