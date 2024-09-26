from django.contrib.auth.backends import ModelBackend
from authentication.models import User

class EmailBackend(ModelBackend):
    def authenticate(self, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
        return None