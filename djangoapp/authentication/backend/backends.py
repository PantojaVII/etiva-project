from django.contrib.auth.backends import ModelBackend
from ..models import User  # Certifique-se de que o caminho está correto

class EmailBackend(ModelBackend):
    def authenticate(self, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
            # Verifica se o usuário está ativo
            if user.is_active and user.check_password(password):
                return user
        except User.DoesNotExist:
            return None  # O usuário não existe
        return None  # Senha incorreta ou usuário inativo
