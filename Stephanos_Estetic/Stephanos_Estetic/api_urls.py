from django.urls import include, path

urlpatterns = [
    path('', include('SE_services.urls')),
    path('', include('SE_donations.urls')),
    path('', include('SE_sales.urls')),
    path('', include('SE_contact.urls')),
    path('', include('SE_users.urls')),  # <-- SE_users define /api/... aquí, sin duplicar abajo
    path('payments/', include(('SE_payments.urls', 'payments'), namespace='payments')),
]
