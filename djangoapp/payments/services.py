# payments/services.py
import mercadopago # type: ignore
from django.conf import settings
import json
import os
from .models import Payment
from django.http import JsonResponse
from credits.models import *
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

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
            "metadata": {
                'payment_pk': payment_id,
                },
            'notification_url': f"https://b3af-2804-61d0-1062-9001-cd0e-d9e4-fb9b-ab53.ngrok-free.app/api/v1/payments/webhook/"

        }

        result = self.sdk.preference().create(payment_data)
        print('-------Criação page payment-------------')
        print(json.dumps(result, indent=4))
        # Verifique se a resposta do MercadoPago foi bem-sucedida
        if result.get('status') == 201:
            payment = result['response']
            init_payment = payment.get('init_point', '')

            # Atualiza o campo 'data' do modelo Payment com a resposta do MercadoPago
            payment_instance = Payment.objects.get(id=payment_id)
            payment_instance.data = result  # Atualiza o campo 'data' com a resposta completa
            payment_instance.payment_id = None  # Atualiza o payment_id no banco
            payment_instance.save()
            
            return init_payment
        else:
            error_message = result.get('response', {}).get('message', 'Erro desconhecido ao criar pagamento')
            raise Exception(f"Erro ao criar pagamento no MercadoPago: {error_message}")
        
        
class ProcessPayment:
    
    def __init__(self, payment_pk, payment_id, payment_info):
        self.payment_pk = payment_pk
        self.payment_id = payment_id
        self.payment_info = payment_info
        self.amount = self.payment_info['transaction_amount']
        self.status = self.payment_info['status']
        try:
            self.payment_obj = Payment.objects.get(id=self.payment_pk)
        except ObjectDoesNotExist:
            print('pagamento não encontrado')
            return JsonResponse({'status': 'Pagamento não encontrado'}, status=404)
    
    # Função principal de criação ou atualização de pagamento
    def process_payment(self):
        validation_response = self.validate_payment_info()
        if validation_response:
            return validation_response
        status = self.status
        # Verifica o status e chama a função correspondente
        if status == "approved":
            return self.handle_approved_payment()
        elif status == "rejected":
            return self.handle_rejected_payment()
        elif status == "in_process":
            return self.handle_pending_payment()
        elif status == "refunded":
            return self.handle_refunded_payment()
        elif status == "cancelled":
            return self.handle_cancelled_payment()
        else:
            print("Status não reconhecido:", status)
            return JsonResponse({'status': 'Status de pagamento não reconhecido'}, status=400)

    # Valida se o pagamento é válido e retorna erro, se necessário
    def validate_payment_info(self):
        if not self.payment_pk:
            return JsonResponse({'status': 'Pagamento inválido: ID ausente'}, status=400)

        if not self.payment_info or 'transaction_amount' not in self.payment_info:
            return JsonResponse({'status': 'Informações de pagamento incompletas'}, status=400)

        return None  # Validação bem-sucedida

    # Verifica se o pagamento já foi aprovado
    def is_payment_already_approved(self):
        if self.payment_obj.status == 'approved':
            print('Pagamento já foi creditado')
            return JsonResponse({'status': 'Pagamento já creditado'}, status=200)
        return False

    # Trata o pagamento aprovado
    def handle_approved_payment(self):
        # Verifica se o pagamento já foi aprovado
        already_approved_response = self.is_payment_already_approved()
        if already_approved_response:
            return already_approved_response

        # Valida o status do pagamento
        if self.status == 'approved':     
            print('Creditar pagamento')
            user = self.payment_obj.user
            description = f"Crédito adicionado: Pagamento ID {self.payment_id} de {self.amount} créditos aprovado em {self.payment_obj.updated_at.strftime('%d/%m/%Y')}."

            # Atualiza o objeto de pagamento
            self.payment_obj.status = 'approved'
            self.payment_obj.payment_id = self.payment_id
            self.payment_obj.data = self.payment_info
            self.payment_obj.save()  # Atualiza o status do pagamento para aprovado

            # Cria a transação de crédito
            CreditTransaction.objects.create(user=user, transaction_type='ADD', amount=self.amount, description=description)
            return JsonResponse({'status': 'Pagamento creditado com sucesso'}, status=200)

        else:
            print('Pagamento não aprovado!')
            return JsonResponse({'status': 'Pagamento não aprovado'}, status=200)

    # Lida com os diferentes status de pagamento
    def handle_rejected_payment(self):
        print('Pagamento rejeitado.')
        # Atualiza o objeto de pagamento
        self.payment_obj.status = 'rejected'
        self.payment_obj.payment_id = self.payment_id
        self.payment_obj.data = self.payment_info
        self.payment_obj.save()  # Atualiza o status do pagamento para aprovado
        return JsonResponse({'status': 'Pagamento rejeitado'}, status=200)

    def handle_pending_payment(self):
        print('Pagamento em processamento.')
        # Atualiza o objeto de pagamento
        self.payment_obj.payment_id = self.payment_id
        self.payment_obj.data = self.payment_info
        self.payment_obj.save()  # Atualiza o status do pagamento para aprovado
        return JsonResponse({'status': 'Pagamento pendente'}, status=200)

    def handle_refunded_payment(self):
        print('Pagamento reembolsado.')
        return JsonResponse({'status': 'Pagamento reembolsado'}, status=200)

    def handle_cancelled_payment(self):
        print('Pagamento cancelado.')
        return JsonResponse({'status': 'Pagamento cancelado'}, status=200)

