from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('Stephanos_Estetic.api_urls')),
    path("api/", include(("SE_services.urls", "booking"), namespace="booking")),
]