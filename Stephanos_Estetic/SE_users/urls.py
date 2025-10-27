# SE_users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("csrf/", views.csrf_view, name="csrf"),          # GET
    path("register/", views.register_view, name="register"),  # POST
    path("login/", views.login_view, name="login"),       # POST
    path("logout/", views.logout_view, name="logout"),    # POST
    path("profile/", views.profile_view, name="profile"), # GET/PUT (si lo sirves bajo /accounts/)
]
