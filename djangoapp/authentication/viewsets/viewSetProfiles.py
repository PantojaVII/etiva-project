from ..models import Profile, User
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from ..serializers.serializerProfiles import ProfileSerializer
from ..validators.validatorsProfiles import ValidatorsProfiles
from utils.common import decode_id, encode_id
from utils.paths.usersFiles import UserFileManager
from rest_framework.decorators import action
from credits.models import ServiceUsage, UserCredit, CreditTransaction, Service
from credits.serializers.service_usage_serializer import ServiceUsageSerializer
from credits.serializers.user_credit_serializer import UserCreditSerializerNoUser
from credits.serializers.credit_transaction_serializer import CreditTransactionNoUserSerializer
from rest_framework.pagination import PageNumberPagination
from decimal import Decimal

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_object(self, pk):
        # Decodifica o hash para obter o ID
        decoded_id = decode_id(pk)
        """ Validando user"""
        data = {"id": decoded_id}
        validator = ValidatorsProfiles(data)
        errors = validator.validate_Profile()
        if errors:
            raise ValidationError(errors)

        return Profile.objects.get(user_id=decoded_id)

    def retrieve(self, request, pk=None, *args, **kwargs):
        profile = self.get_object(pk)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """ Pegando DADOS ENVIADOS """
        encoded_id = request.data.get('user')
        decoded_id = decode_id(encoded_id)
        
        # Substitui o valor de 'user' em request.data com o decoded_id
        request.data['user'] = decoded_id
        
        data = request.data
        
        """ Validações """
        validator = ValidatorsProfiles(data)
        errors = validator.validate_CadProfile()
        
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Se um novo arquivo de avatar foi enviado
        if 'avatar' in request.FILES:
            file = request.FILES['avatar']
            uploader = UserFileManager(file=file, hash_id=encoded_id)
            # Salva o arquivo localmente
            saved_path = uploader.upload_files_local(uploader.path_avatar())
            
            data['picture'] = saved_path

        # Crie uma instância do serializer com os dados enviados
        serializer = self.serializer_class(data=data, context={'request': request})
       
        """ Salvando """
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop('password_confirmation', None)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, pk=None, *args, **kwargs):
        profile = self.get_object(pk)

        # Acesse os dados diretamente, sem copiar
        data = {key: value for key, value in request.data.items() if key != 'avatar'}
        
        # Verifique se o arquivo está em request.FILES
        avatar = request.FILES.get('avatar')
        if avatar:
            data['avatar'] = avatar 

        # Valida dados enviados
        validator = ValidatorsProfiles(data)
        errors = validator.validate_UpdateProfile()
        
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Envia o avatar
        fileManager = UserFileManager(request=request, profile=profile)
        picture_path = fileManager.upload_avatar(request)
        if picture_path:
          
            data['picture'] = f"{picture_path}"

        serializer = self.serializer_class(profile, data=data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object(pk)
        
        uploader = UserFileManager(hash_id=pk)
        uploader.delete_directory_local(uploader.path_user())
        
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    #------------------------End points de apps exclusivos da aplicação------------------------
    """ Buscamos todos os serviços usados pelo usuário """
    @action(detail=True, methods=['get'], url_path='service-usage')
    def service_usage(self, request, pk=None):
        profile = self.get_object(pk)
        
        # Verifica se um slug de serviço específico foi fornecido na URL
        service_slug = request.query_params.get('service', None)
        
        # Filtra os serviços utilizados pelo usuário
        if service_slug:
            # Se um service_slug for fornecido, filtra por esse slug
            service_usages = ServiceUsage.objects.filter(user=profile.user, service__slug=service_slug).order_by('-used_at')
            # Busca o nome do modelo associado ao serviço
            try:
                service = Service.objects.get(slug=service_slug)
                model_name = service.name
                pk_service = encode_id(service.id)
                cost_in_credits = Decimal(service.cost_in_credits)
            except Service.DoesNotExist:
                return Response({"error": "Serviço não encontrado."}, status=404)
        else:
            # Caso contrário, retorna todos os serviços utilizados
            service_usages = ServiceUsage.objects.filter(user=profile.user).order_by('-used_at')
            model_name = None  # Nenhum modelo específico, já que não há filtro

        # Instancia um paginador
        paginator = PageNumberPagination()

        # Pagina o queryset
        result_page = paginator.paginate_queryset(service_usages, request)

        # Serializa os resultados paginados
        serializer = ServiceUsageSerializer(result_page, many=True)

        # Adiciona o nome do modelo à resposta
        response_data = paginator.get_paginated_response(serializer.data)
        if model_name:
            response_data.data['name'] = model_name
            response_data.data['pk_service'] = pk_service  
            response_data.data['cost_in_credits'] = cost_in_credits  
        
        # Retorna a resposta paginada
        return response_data

    """ Faz um resumo apenas do saldo de créditos do usuário. """
    @action(detail=True, methods=['get'], url_path='credit-amount')
    def credit_amount(self, request, pk=None):
        profile = self.get_object(pk)
        
        try:
            # Tenta obter o UserCredit do usuário
            user_credit = UserCredit.objects.get(user=profile.user)
        except UserCredit.DoesNotExist:
            # Se o usuário não tiver créditos, cria um objeto temporário com saldo 0
            user_credit = UserCredit(user=profile.user, balance=0)

        # Serializa o saldo de crédito do usuário
        credit_serializer = UserCreditSerializerNoUser(user_credit)
        
        # Monta a resposta contendo apenas o saldo de créditos
        response_data = {
            'amount': credit_serializer.data  # Apenas o saldo de créditos
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    """ Faz um resumo dos créditos do usuário. """
    @action(detail=True, methods=['get'], url_path='credit-summary')
    def credit_summary(self, request, pk=None):
        profile = self.get_object(pk)
        
        # Obtém ou cria UserCredit para o usuário
        user_credit = UserCredit.objects.get_or_create(
            user=profile.user,
            defaults={'balance': 0}  # Define o saldo padrão como 0
        )

        # Serializa o saldo de crédito do usuário
        credit_serializer = UserCreditSerializerNoUser(user_credit)

        # Obtém ou cria o último uso de serviço do usuário
        last_service_usage = ServiceUsage.objects.get_or_create(user=profile.user)

        # Serializa o último serviço utilizado
        last_service_usage_serializer = ServiceUsageSerializer(last_service_usage)
        
        # Monta a resposta
        response_data = {
            'amount': credit_serializer.data,
            'last_service': last_service_usage_serializer.data,  # Sempre terá dados do último serviço utilizado
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    """ Obtém as transações de crédito do usuário. """
    @action(detail=True, methods=['get'], url_path='credit-transactions')
    def credit_transactions(self, request, pk=None):
        profile = self.get_object(pk)

        # Obtém o termo de busca da query parameter, se existir
        search_term = request.query_params.get('search', '')

        # Ordena as transações do mais novo para o mais velho
        transactions = CreditTransaction.objects.filter(user=profile.user)

        # Se um termo de busca foi fornecido, filtra as transações
        if search_term:
            transactions = transactions.filter(description__icontains=search_term)

        # Instancia um paginador
        paginator = PageNumberPagination()
    

        # Pagina o queryset
        result_page = paginator.paginate_queryset(transactions.order_by('-created_at'), request)

        # Serializa os resultados paginados
        serializer = CreditTransactionNoUserSerializer(result_page, many=True)

        # Retorna a resposta paginada
        return paginator.get_paginated_response(serializer.data)