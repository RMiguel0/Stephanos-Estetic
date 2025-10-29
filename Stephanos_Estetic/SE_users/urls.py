# SE_users/urls.py
from django.urls import path
from .views import csrf_view, current_user, logout_api, ProfileView, UserOrdersView

urlpatterns = [
    path("auth/csrf/", csrf_view, name="api-csrf"),
    path("user/me/", current_user, name="api-user-me"),
    path("auth/logout/", logout_api, name="api-logout"),
    path("profile/", ProfileView.as_view(), name="api-profile"),
    path("orders/", UserOrdersView.as_view(), name="api-user-orders"),
]
