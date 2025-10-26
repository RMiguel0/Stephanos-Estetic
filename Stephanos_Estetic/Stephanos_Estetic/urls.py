from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  # login/logout/password
    path("accounts/", include("SE_users.urls")),             # register
    path('api/', include('Stephanos_Estetic.api_urls')),
]