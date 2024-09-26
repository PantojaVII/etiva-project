from django.contrib.auth.views import PasswordResetView
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from utils.common import encode_id
User = get_user_model()

class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data['email']
        users = User.objects.filter(email=email)  # Filtra usuários pelo e-mail
        
        for user in users:
            refresh = RefreshToken.for_user(user)
            context = {
                'email': email,
                'domain': self.request.get_host(), #para onde o usuário vai
                'pk': encode_id(user.id),
                'token': str(refresh.access_token),
                'protocol': 'https' if self.request.is_secure() else 'http',
            }
            
            subject = "Redefinição de senha"
            email_body = render_to_string('registration/password_reset.html', context)
            send_mail(subject, email_body, None, [email], html_message=email_body)

        return JsonResponse({
            "message": "Um e-mail de redefinição de senha foi enviado com sucesso.",
            "status": "success"
        }, status=200)

    def form_invalid(self, form):
        return JsonResponse({
            "message": "Ocorreu um erro ao tentar redefinir a senha. Verifique o e-mail informado.",
            "status": "error"
        }, status=400)

