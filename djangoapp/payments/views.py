from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse
from .services import MercadoPagoService, ProcessPayment
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
import mercadopago # type: ignore
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Payment 
 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_page_payment(request):
    try:
        # Obtenha o usuário autenticado
        user = request.user
 
        # Obtenha e valide a quantidade de créditos a partir do formulário
        quantity = int(request.data.get('quantity', 1))
        if quantity <= 0:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)

        # Crie uma instância do serviço MercadoPago
        mercado_pago_service = MercadoPagoService()

        # Calcule o valor total (por exemplo, 1 BRL por crédito)
        amount = quantity * 1  # Supondo que cada crédito custa 1 BRL

        # Crie um registro de pagamento no banco de dados
        payment = Payment.objects.create(user=user, amount=amount, status='pending', payment_id=None)
 

        # Crie o pagamento com o valor calculado
        init_payment_url = mercado_pago_service.create_payment(quantity=amount, payment_id=payment.id)
        if not init_payment_url:
            payment.status = 'failed'
            payment.save()
            return JsonResponse({'error': 'Failed to create payment'}, status=500)

        # Redirecione o usuário para o pagamento

        return JsonResponse({'paymentUrl': init_payment_url}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Função que obtém as informações detalhadas de um pagamento
def get_payment_info(payment_id):
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)   
    # Faz a requisição para obter os detalhes do pagamento pelo ID
    payment_info = sdk.payment().get(payment_id)
  
    return payment_info['response']

# View para processar notificações do webhook
@csrf_exempt  # Desativa a verificação de CSRF para essa view, permitindo requisições externas
def process_payment(request):
    if request.method == 'POST':
        try:
            print('----------------- Inicio da requisição -----------------')
            # Decodifica o corpo da requisição em JSON
            data = json.loads(request.body)
            
            # Extrai o ID do pagamento da estrutura JSON recebida
            payment_id = data.get('data', {}).get('id')
            
            # Extrai a ação que foi realizada (ex: "payment.updated" ou "payment.created")
            action = data.get('action')
            
            # Verifica se o action existe e se o payment_id está presente
            if action and payment_id:
                payment_info = get_payment_info(payment_id)
                print('----------action------------')
                print(action)
                """ É acionado quando é criado um novo pagamento, seja ele aprovado ou não """
                if action == 'payment.created':
                    # Lógica para quando o pagamento é criado
                    print("Pagamento criado com sucesso:", json.dumps(payment_info, indent=4))
                    
                    # Certifique-se de que o 'metadata' e 'payment_pk' existem no 'payment_info'
                    if 'metadata' in payment_info and 'payment_pk' in payment_info['metadata']:
                        pk = payment_info['metadata']['payment_pk']
                        process_payment = ProcessPayment(pk, payment_id, payment_info=payment_info)
                        process_payment.process_payment()
                        return JsonResponse({'status': 'Pagamento processado'}, status=202)
                    else:
                        return JsonResponse({'error': 'Metadata ou payment_pk não encontrado'}, status=200)
                
                elif action == 'payment.updated':
                    status = payment_info['status']
                    print('----------status------------')
                    print(status)
                    # Cria uma instância de ProcessPayment
                    process_payment = ProcessPayment(payment_info['metadata']['payment_pk'], payment_id, payment_info)
                    
                    # Atualiza o pagamento com base no status
                    response = process_payment.process_payment()
                    
                    print("Pagamento atualizado:", json.dumps(payment_info, indent=4))
                    
                    return response  # Retorna a resposta da atualização do pagamento

                elif action == 'payment.approved':
                    # Se o pagamento foi aprovado, processa o pagamento aprovado
                    print("Pagamento aprovado:", payment_info)
                    return JsonResponse({}, status=200)

                elif action == 'payment.rejected':
                    # Se o pagamento foi rejeitado, processa o pagamento rejeitado
                    print("Pagamento rejeitado:", payment_info)
                    return JsonResponse({'status': 'ok'}, status=200)

                elif action == 'payment.pending':
                    # Lógica para pagamento pendente
                    print("Pagamento pendente:", payment_info)
                    return JsonResponse({'status': 'Pagamento pendente processado'}, status=200)

                elif action == 'payment.refunded':
                    # Lógica para quando o pagamento é reembolsado
                    print("Pagamento reembolsado:", payment_info)
                    return JsonResponse({'status': 'Pagamento reembolsado processado'}, status=200)

                elif action == 'payment.cancelled':
                    # Lógica para quando o pagamento é cancelado
                    print("Pagamento cancelado:", payment_info)
                    return JsonResponse({'status': 'Pagamento cancelado processado'}, status=200)

                # Caso a ação não seja reconhecida
                else:
                    print("Ação não reconhecida:", action)
                    return JsonResponse({'status': 'Ação não reconhecida'}, status=400)

            # Retorna uma resposta de erro caso o payment_id não esteja presente
            print("ID de pagamento não encontrado:", action)
            return JsonResponse({'error': 'ID de pagamento não encontrado'}, status=200)

        except json.JSONDecodeError:
            print("JSON inválido:", action)
            
            # Retorna erro caso o corpo da requisição não seja um JSON válido
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        except Exception as e:
            print("Erro inesperado:", str(e))
            # Captura quaisquer outros erros inesperados e os retorna na resposta,
            return JsonResponse({'error': str(e)}, status=500)

    # Caso o método HTTP da requisição não seja POST, retorna um erro de método inválido
    return JsonResponse({'error': 'Método de requisição inválido'}, status=405)