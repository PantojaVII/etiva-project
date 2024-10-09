# payments/urls.py
from django.urls import path
from . import views
from .views import create_payment, payment_success, payment_failure, payment_pending, process_payment

urlpatterns = [
    path('payments/create/', views.create_payment, name='create_payment'),
 
    path('payments/success/', payment_success, name='payment_success'),
    path('payments/failure/', payment_failure, name='payment_failure'),
    path('payments/pending/', payment_pending, name='payment_pending'),
    path('payments/webhook/', process_payment, name='mercadopago_webhook'),

]
