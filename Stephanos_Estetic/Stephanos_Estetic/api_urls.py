from django.urls import include, path
from SE_users.views import google_login_view

urlpatterns = [
    path('', include('SE_services.urls')),
    path('', include('SE_donations.urls')),
    path('', include('SE_sales.urls')),
    path('', include('SE_contact.urls')),
    path('payments/', include(('SE_payments.urls', 'payments'), namespace='payments')),
    path('auth/google/', google_login_view, name='api-auth-google'),
]
