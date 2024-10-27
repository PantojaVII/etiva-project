import requests
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from ..models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from ..validators.validatorsUsers import ValidatorUser

class CustomTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        # Obtenha o email e a senha do corpo da requisição
        email = request.data.get("email")
        password = request.data.get("password")
        
        # Valida dados enviados
        validator = ValidatorUser({"email": email, "password": password})
        errors = validator.validate_login_credentials()
        
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Verifica se o usuário existe e está ativo
        user = authenticate(email=email, password=password)
        
        if user is not None:
            # Aqui você pode gerar e retornar o token
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })


""" Com google """
class GoogleRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')

        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Valida o token do Google
        google_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        google_response = requests.get(google_url)
        if google_response.status_code != 200:
            return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)

        google_data = google_response.json()
        
        # Extraia as informações necessárias do token
        email = google_data.get('email')
        sub = google_data.get('sub')
        first_name = google_data.get('given_name')
        last_name = google_data.get('family_name')
        picture = google_data.get('picture')
        phone_number = request.data.get('phone_number')
        data_of_birth = request.data.get('data_of_birth')

        if not email or not sub:
            return Response({"error": "Invalid token data"}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica se o usuário já existe
        if User.objects.filter(email=email).exists():
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Cria o usuário
        user = User.objects.create(
            username=sub,
            email=email,
            first_name=first_name,
            last_name=last_name,
            picture=picture,
            phone_number=phone_number,
            data_of_birth=data_of_birth,
            auth_method="google"
        )
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')

        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Valida o token do Google
        google_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        google_response = requests.get(google_url)
        if google_response.status_code != 200:
            return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)

        google_data = google_response.json()
        
        # Extraia as informações necessárias do token
        email = google_data.get('email')
        sub = google_data.get('sub')

        if not email or not sub:
            return Response({"error": "Invalid token data"}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica se o usuário existe
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found, please register first"}, status=status.HTTP_404_NOT_FOUND)

        # Gera um JWT para esse usuário
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


        
    




