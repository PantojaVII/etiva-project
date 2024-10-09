from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.response import Response
from authentication.validators.validatorsUsers import ValidatorUser
from utils.common import encode_id
import os 
from datetime import timedelta

User = get_user_model()

class CustomPasswordResetAPIView(APIView):
    permission_classes = [AllowAny]  # Permite que qualquer um acesse esta view

    def post(self, request):
        data = request.data
        data['csrf'] = request.headers.get('x-csrftoken')
        # Valida dados enviados
        validator = ValidatorUser(data=data)
        errors = validator.validate_RestorePassword()
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        email = request.data.get('email')
        users = User.objects.filter(email=email) 
        
        for user in users:
            refresh = RefreshToken.for_user(user)
            # Cria um token de acesso com validade de 1 minuto
            access_token = AccessToken.for_user(user)
            access_token.set_exp(lifetime=timedelta(minutes=1))  # Define a expiração para 1 minuto
            
            context = {
                'email': email,
                'domain': os.getenv('HOST_FRONT_END'),  # para onde o usuário vai
                'pk': encode_id(user.id),  # Codifica o ID do usuário
                'token': str(access_token),  # Usando o token de acesso personalizado
                'protocol': 'https' if request.is_secure() else 'http',
            }
            
            subject = "Redefinição de senha"
            email_body = render_to_string('registration/password_reset.html', context)
            send_mail(subject, email_body, None, [email], html_message=email_body)

        return Response(
            {"message": "Um e-mail de redefinição de senha foi enviado com sucesso."},
            status=status.HTTP_200_OK
        )

