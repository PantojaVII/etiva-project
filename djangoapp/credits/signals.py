from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User  # Importa o modelo User do Django
from .models import UserCredit  # Importa o modelo UserCredit definido no mesmo aplicativo

# Define um sinal que será acionado após um objeto User ser salvo
@receiver(post_save, sender=User)
def create_user_credit(sender, instance, created, **kwargs):
    # O sinal 'post_save' é acionado após a criação ou atualização de um User
    if created:  # Verifica se o objeto User foi criado (ou seja, é um novo usuário)
        # Cria uma nova instância de UserCredit associada ao novo usuário
        UserCredit.objects.create(user=instance)
