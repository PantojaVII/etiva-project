from django.contrib import admin
from .models import Payment

#@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'payment_id', 'created_at', 'updated_at')
    search_fields = ('user__username', 'status', 'payment_id')
    list_filter = ('status', 'created_at', 'updated_at')

