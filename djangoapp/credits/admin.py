from django.contrib import admin
from .models import UserCredit, CreditTransaction, Service, ServiceUsage
from django.contrib import messages
from django.core.exceptions import ValidationError

# Configuração de exibição do modelo UserCredit
@admin.register(UserCredit)
class UserCreditAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'created_at', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    # Remove a opção de adicionar novos registros
    def has_add_permission(self, request):
        return False

    # Permite edição dos registros existentes
    def has_change_permission(self, request, obj=None):
        return False

    # Permite a exclusão dos registros, se necessário
    def has_delete_permission(self, request, obj=None):
        return True

# Configuração de exibição do modelo CreditTransaction
@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'created_at', 'description')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at',)
    list_filter = ('transaction_type', 'created_at')
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        user_credit, created = UserCredit.objects.get_or_create(user=obj.user)

        if obj.transaction_type == 'ADD':
            user_credit.add_credits(obj.amount)
            messages.success(request, "Credits added successfully.")
            super().save_model(request, obj, form, change)  # Salva a transação
        elif obj.transaction_type == 'DEDUCT':
            if not user_credit.deduct_credits(obj.amount):
                messages.error(request, "Insufficient credits.")
                return  # Não salva a transação se falhar
            else:
                messages.success(request, "Credits deducted successfully.")
                super().save_model(request, obj, form, change)  # Salva a transação

                
# Configuração de exibição do modelo Service
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost_in_credits','cost_in_generate','profit', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_active', 'created_at', 'updated_at')
    ordering = ('name',)

# Configuração de exibição do modelo ServiceUsage
@admin.register(ServiceUsage)
class ServiceUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'credits_used', 'used_at')
    search_fields = ('user__username', 'service__name')
    readonly_fields = ('used_at',)
    list_filter = ('used_at',)
    ordering = ('-used_at',)


