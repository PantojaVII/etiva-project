from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from utils.common import *
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('Users should have a username')
        if email is None:
            raise TypeError('Users should have a Email')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None):
        if password is None:
            raise TypeError('Password should not be none')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    AUTH_METHOD_CHOICES = [
        ('seek', _('Seek')),
        ('google', _('Google')),
        ('facebook', _('Facebook')),
        ('microsoft', _('Microsoft')),
        ('email', _('Email')),
        # Adicione outros métodos se necessário
    ]
    username = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    auth_method = models.CharField(
        max_length=20,
        choices=AUTH_METHOD_CHOICES,
        default='seek'
    )
    objects = UserManager()
    
    def save(self, *args, **kwargs):
        if self.pk:  # se o usuário já existe (atualização)
            user = User.objects.get(pk=self.pk)
            
            if self.password != user.password:  # se a senha foi alterada
                self.set_password(self.password)
        else:  # se for um novo usuário

            self.set_password(self.password)

        super().save(*args, **kwargs)
    def __str__(self):
        return self.email


#Informações adicionais ficarão aqui
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=False, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    picture = models.CharField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - Profile"

