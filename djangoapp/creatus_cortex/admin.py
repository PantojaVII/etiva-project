from django.contrib import admin
from .models import GeneratedImage

class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'image_url', 'prompt', 'created_at')  # Campos a serem exibidos na lista
    search_fields = ('user__username', 'prompt')  # Campos pesquisáveis
    list_filter = ('created_at',)  # Filtros disponíveis na interface do admin
    ordering = ('-created_at',)  # Ordenação padrão

# Registra o modelo no admin
admin.site.register(GeneratedImage, GeneratedImageAdmin)
