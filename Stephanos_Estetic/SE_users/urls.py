# SE_users/urls.py
from django.urls import path
from .views import csrf_view, current_user, logout_api

urlpatterns = [
    path("api/auth/csrf/", csrf_view, name="csrf"),
    path("api/user/me/", current_user, name="current_user"),
    path("api/auth/logout/", logout_api, name="logout_api"),
]
