from django.urls import include, path

urlpatterns = [
    path('', include('SE_services.urls')),
    path('', include('SE_donations.urls')),
    path('', include('SE_sales.urls')),
    path('', include('SE_contact.urls')),
    path('payments/', include(('SE_payments.urls', 'payments'), namespace='payments')),
]
