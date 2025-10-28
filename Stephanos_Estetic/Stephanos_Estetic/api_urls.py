# Stephanos_Estetic/api_urls.py
from django.urls import include, path
from SE_users.views import (
    csrf_view,      # GET: setea cookie CSRF
    current_user,   # GET: usuario autenticado
    # register_view,
    # login_view,
    # logout_view,
    # profile_view,
    # google_login_view,
)

urlpatterns = [
    path('', include('SE_services.urls')),
    path('', include('SE_donations.urls')),
    path('', include('SE_sales.urls')),
    path('', include('SE_contact.urls')),
    path('', include('SE_users.urls')),
    path('payments/', include(('SE_payments.urls', 'payments'), namespace='payments')),

    # --- Endpoints API que sí usamos ahora ---
    path('auth/csrf/', csrf_view, name='api-csrf'),        # GET
    path('user/me/', current_user, name='api-user-me'),    # GET (401 si no hay sesión)

    # Si más adelante reactivas estos endpoints, descoméntalos junto
    # con sus imports arriba:
    # path('auth/register/', register_view, name='api-register'),
    # path('auth/login/', login_view, name='api-login'),
    # path('auth/logout/', logout_view, name='api-logout'),
    # path('profile/', profile_view, name='api-profile'),
    # path('auth/google/', google_login_view, name='api-auth-google'),
]
