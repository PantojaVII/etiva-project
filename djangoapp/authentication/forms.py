from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User

class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'is_staff')

    def clean_password(self):
        # Independentemente do que o usuário fornecer, o valor da senha será aquele que está no banco de dados.
        return self.initial["password"]
