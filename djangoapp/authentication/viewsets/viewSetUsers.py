from .viewSetProfiles import ProfileViewSet
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from ..serializers.serializerUsers import UserSerializer
from utils.common import decode_id, encode_id
from ..validators.validatorsUsers import ValidatorUser
from rest_framework.request import Request
from django.utils.text import slugify
from ..models import User, Profile
import random
import string
import jwt  
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from utils.common import decode_id, encode_id
from utils.paths.baseFileUploader import BaseFileUploader 
from rest_framework.decorators import action
from django.conf import settings

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


    def get_object(self, pk):
        # Decodifica o hash para obter o ID
        decoded_id = decode_id(pk)

        """ Validando user """
        data = {"id": decoded_id}
        validator = ValidatorUser(data)
        errors = validator.validate_User()
        if errors:
            raise ValidationError(errors)

        return User.objects.get(id=decoded_id)

    def create(self, request, *args, **kwargs):
        """ Cadastrando User """
        user_data = request.data
        user_data['username'] = self.generate_unique_username(user_data.get('email', ''))

        # Validações do Usuário
        validator = ValidatorUser(user_data)
        errors = validator.validate_CadUser()
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Cria o usuário
        user_serializer = self.serializer_class(data=user_data, context={'request': request})
        user_serializer.is_valid(raise_exception=True)
        user_serializer.validated_data.pop('password_confirmation', None)
        self.perform_create(user_serializer)
        # Inicializa a variável do usuário
        user_instance = user_serializer.instance
        
        try:
            request.data['user'] = encode_id(user_instance.id)
            # Criando o perfil associado ao usuário
            profile_viewset = ProfileViewSet()
            response = profile_viewset.create(request=request)

            # Verifica a resposta do perfil
            if response.status_code == status.HTTP_201_CREATED:
                return Response(user_serializer.data, status=status.HTTP_201_CREATED)
            else:
                user_instance.delete()  # Remove o usuário criado se falhar ao criar o perfil
                return Response(response.data, status=response.status_code)

        except Exception as e:
            # Em caso de exceção, remove o usuário criado e retorna erro
            if user_instance:
                user_instance.delete()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None, *args, **kwargs):
        user = self.get_object(pk)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def update(self, request, pk=None, *args, **kwargs):
        user = self.get_object(pk)
        authorization_header = request.headers.get('Authorization')
        # Crie uma cópia mutável dos dados da solicitação
        data = request.data.copy()

        # Adiciona o id na requisição para fazer a validação
        data['id'] = user.id
        
        # Valida dados enviados
        validator = ValidatorUser(user=user, data=data)
        errors = validator.validate_UpdateUser(authorization_header)
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(user, data=data, context={'request': request}, partial=True)

        # Prepara para atualização
        serializer.is_valid(raise_exception=True)


        # Salva os dados atualizados
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object(pk)
        print("---------------")
        path = f"users/{encode_id(instance.id)}"
        uploader = BaseFileUploader()
        uploader.delete_directory_local(path)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        # Define permissões baseadas no método HTTP da solicitação
        if self.request.method == 'POST':
            return [AllowAny()]  # Permite que qualquer um acesse o método POST (criação)
        return [permission() for permission in self.permission_classes]

    def generate_unique_username(self, email):
        # Extrai a parte do e-mail antes do '@'
        base_username = slugify(email.split('@')[0])
        
        # Limita o comprimento do username a um tamanho adequado (opcional)
        base_username = base_username[:30]
        
        # Verifica se o username já existe
        username = base_username
        counter = 1
        
        while User.objects.filter(username=username).exists():
            # Gera um sufixo numérico ou alfanumérico para garantir unicidade
            suffix = ''.join(random.choices(string.digits, k=4))  # Exemplo: '1234'
            username = f'{base_username}_{suffix}'
            counter += 1
            
            # Evita um loop infinito em caso de um grande número de conflitos (muito improvável)
            if counter > 1000:
                raise Exception('Não foi possível gerar um username único.')

        return username
    
    @action(detail=True, methods=['post', 'put'], url_path='password-reset/confirm', permission_classes=[IsAuthenticated])
    def password_reset_confirm(self, request, pk=None, *args, **kwargs):
        user = self.get_object(pk)  # Certifique-se de que este método funcione corretamente
        authorization_header = request.headers.get('Authorization')

        # Crie uma cópia mutável dos dados da solicitação
        data = request.data.copy()

        # Valida dados enviados
        validator = ValidatorUser(user=user, data=data)
        errors = validator.validate_ResetPassword(authorization_header)
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Lógica de redefinição de senha aqui
        serializer = self.serializer_class(user, data=data, context={'request': request}, partial=True)

        # Prepara para atualização
        serializer.is_valid(raise_exception=True)


        # Salva os dados atualizados
        serializer.save()
        return Response(serializer.data)

    
class UserDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        try:
            profile = user.profile  # Acesso ao perfil do usuário
        except Profile.DoesNotExist:
            profile = None

        base_url = request.build_absolute_uri('/media/')
        user_data = {
            "pk": encode_id(user.id),
            "username": user.username,
            "user_email": user.email,
            "first_name": profile.first_name if profile else None,
            "last_name": profile.last_name if profile else None,
            "picture": f"{base_url}{profile.picture}" if profile and profile.picture else None,
            "phone_number": profile.phone_number if profile else None,
            "date_of_birth": profile.date_of_birth if profile else None,
        }
        return Response(user_data)

