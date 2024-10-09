# payments/services.py
import mercadopago # type: ignore
from django.conf import settings
import json
import os

class MercadoPagoService:
    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)  # Certifique-se de que o token está configurado

    def create_payment(self, quantity, payment_id):
        
        payment_data = {
            "items": [
                {
                    'id': "1",
                    'title': 'Créditos',
                    'description': 'Compra de créditos na plataforma',
                    'quantity': quantity,
                    'currency_id': 'BRL',
                    'unit_price': 1.00
                }
            ],
            "back_urls": {
                "success": f"{settings.HOST_API}/api/v1/payments/success",
                "failure": f"{settings.HOST_API}/api/v1/payments/failure",
                "pending": f"{settings.HOST_API}/api/v1/payments/pending"
            },
            'notification_url': f"https://bb31-2804-61d0-1062-9001-1317-54d7-200b-ba09.ngrok-free.app/api/v1/payments/webhook/?payment_id={payment_id}"

        }

        result = self.sdk.preference().create(payment_data)

        # Verifique se a resposta do MercadoPago foi bem-sucedida
        if result.get('status') == 201:
            payment = result['response']
            init_payment = payment.get('init_point', '')
            return init_payment
        else:
            error_message = result.get('response', {}).get('message', 'Erro desconhecido ao criar pagamento')
            raise Exception(f"Erro ao criar pagamento no MercadoPago: {error_message}")
