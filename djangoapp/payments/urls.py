# payments/urls.py
from django.urls import path
from . import views
from .views import create_page_payment, process_payment

urlpatterns = [
    path('payments/create/', create_page_payment, name='create_payment'),
    path('payments/webhook/', process_payment, name='mercadopago_webhook'),
]
