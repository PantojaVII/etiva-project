from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal  
from django.core.exceptions import ValidationError

User = get_user_model()


# Mantém o saldo de créditos de cada usuário
class UserCredit(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='credits')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Balance: {self.balance}"

    def add_credits(self, amount):
        # Garante que a quantidade adicionada é um Decimal
        amount = Decimal(amount)  # Converte para Decimal
        self.balance += amount
        self.save()

    def deduct_credits(self, amount):
        amount = Decimal(amount)
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        else:
            return False
            
class CreditTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('ADD', 'Add'),
        ('DEDUCT', 'Deduct'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_transactions')
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type}: {self.amount}"

    def save(self, *args, **kwargs):
        user_credit, created = UserCredit.objects.get_or_create(user=self.user)

        if self.transaction_type == 'ADD':
            user_credit.add_credits(self.amount)
        elif self.transaction_type == 'DEDUCT':
            if not user_credit.deduct_credits(self.amount):
                return False  # Retorna False para indicar falha na dedução

        super().save(*args, **kwargs)

#define os serviços disponíveis e seus custos em créditos.
class Service(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Nome do serviço
    description = models.TextField(blank=True, null=True)  # Descrição do serviço
    cost_in_credits = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Custo do serviço em créditos
    cost_in_generate = models.DecimalField(max_digits=10, decimal_places=3, default=0.00)  # Custo do serviço em créditos
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Lucro do serviço
    is_active = models.BooleanField(default=True)  # Indica se o serviço está ativo ou não
    created_at = models.DateTimeField(auto_now_add=True)  # Data de criação do registro
    updated_at = models.DateTimeField(auto_now=True)  # Data de atualização do registro
  
    def save(self, *args, **kwargs):
        # Calcula o lucro antes de salvar
        self.profit = self.cost_in_credits - self.cost_in_generate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - Profit: {self.profit} credits"

#registra o uso de serviços pelos usuários e os créditos consumidos.
class ServiceUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_usages')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='usages')
    credits_used = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Service: {self.service.name} - Credits Used: {self.credits_used}"

    def save(self, *args, **kwargs):
        # Chame o método record_usage para registrar o uso
        if self.credits_used and self.user and self.service:
            try:
                # Usar o método record_usage para deduzir os créditos e registrar a transação
                credits_used = self.service.cost_in_credits
                CreditTransaction.objects.create(
                user=self.user,
                transaction_type='DEDUCT',
                amount=credits_used,
                description=f"Uso do serviço: {self.service.name}"
            )
            except ValidationError as e:
                # Se houver um erro, você pode lidar com isso conforme necessário
                raise e  # Levanta o erro para ser tratado pelo chamador
        super().save(*args, **kwargs)


