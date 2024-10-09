from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse
from .services import MercadoPagoService
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
import mercadopago # type: ignore
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Payment 

@api_view(['POST'])  # Decorador necessário para views baseadas em função no Django REST Framework
@permission_classes([IsAuthenticated])  # Requer autenticação com JWT
def create_payment(request):
    try:
        # Obtenha o usuário autenticado
        user = request.user
        print('--------------')
        print(user.id)

        # Obtenha a quantidade de créditos a partir do formulário
        quantity = int(request.data.get('quantity', 1))  # Use request.data para obter dados do corpo da requisição

        # Crie uma instância do serviço MercadoPago
        mercado_pago_service = MercadoPagoService()

        # Calcule o valor total (por exemplo, 1 BRL por crédito)
        amount = quantity * 1  # Supondo que cada crédito custa 1 BRL

        # Crie um registro de pagamento no banco de dados
        payment = Payment.objects.create(user=user, amount=amount, status='pending', payment_id=None)

        print(payment.id)
        # Crie o pagamento com o valor calculado
        init_payment_url = mercado_pago_service.create_payment(quantity=amount, payment_id=payment.id)

        # Retorne o URL de inicialização do pagamento em formato JSON
        return redirect(init_payment_url)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
 
def payment_success(request):
    # Aqui você pode verificar o status do pagamento (opcional)
    # O Mercado Pago pode enviar dados via query params como 'payment_id' e 'status'
    payment_id = request.GET.get('payment_id', '')
    status = request.GET.get('collection_status', '')

    # Valide se o pagamento foi realmente aprovado (status == 'approved')
    if status == 'approved':
        # Exibir uma mensagem de sucesso ou redirecionar
        return HttpResponse("Pagamento bem-sucedido! ID do pagamento: " + payment_id)
    else:
        return HttpResponse("Falha ao processar o pagamento.")

def payment_failure(request):
    return HttpResponse("O pagamento falhou. Por favor, tente novamente.")

def payment_pending(request):
    # Captura informações da URL, como ID do pagamento e status
    payment_id = request.GET.get('payment_id', '')
    status = request.GET.get('collection_status', '')

    # Exibe uma mensagem informando que o pagamento está pendente
    if status == 'in_process' or status == 'pending':
        return HttpResponse(f"Seu pagamento está pendente. ID do pagamento: {payment_id}. Aguarde a confirmação.")
    else:
        return HttpResponse("Erro ao processar o pagamento. Status desconhecido.")
    
def process_payment_approved():
    print('------------------------------')
    print("Função de pós-pagamento foi chamada com sucesso!")

def process_payment_rejected():
    print('------------------------------')
    print("Função de pós-pagamento foi chamada com sucesso! COMPRA REJEITADA")

def get_payment_info(payment_id):
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    # Faz uma requisição para obter os detalhes do pagamento
    payment_info = sdk.payment().get(payment_id)

    # Imprime a resposta para depuração
    print(payment_info)

    if payment_info['status'] == 200:
        return payment_info['response']
    else:
        raise Exception("Erro ao obter informações do pagamento: {}".format(payment_info))



@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        print('---------------')
        print('webhook')
        try:
            # Decodifica o corpo da requisição
            data = json.loads(request.body)

            # Imprime os dados recebidos em formato JSON
            print(json.dumps(data, indent=4))  # Adicionando indentação para melhor legibilidade

            payment_id = data.get('data', {}).get('id')
            action = data.get('action')

            # Verifica o status do pagamento e realiza as ações necessárias
            if action == 'payment.updated' and payment_id:
                payment_info = get_payment_info(payment_id)  # Função para buscar detalhes do pagamento
                status = payment_info.get('status')

                if status == 'approved':
                    # Processar o pagamento aprovado
                    process_payment_approved(payment_info)
                elif status == 'rejected':
                    # Processar o pagamento rejeitado
                    process_payment_rejected(payment_info)
                elif status == 'in_process':
                    # Se o pagamento estiver em processamento, podemos apenas registrar
                    print(f"Pagamento {payment_id} em processamento.")
                else:
                    print(f"Status não tratado: {status}")
            else:
                print(f"Ação não tratada: {action}")

            return JsonResponse({'status': 'ok'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)