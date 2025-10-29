from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Fuerza las rutas "clásicas" a ir por Google
    path("accounts/login/",  RedirectView.as_view(url="/accounts/google/login/")),
    path("accounts/signup/", RedirectView.as_view(url="/accounts/google/login/")),

    # Allauth debe ir después
    path("accounts/", include("allauth.urls")),

    # API
    path("api/", include("Stephanos_Estetic.api_urls")),
]
