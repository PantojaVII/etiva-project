# participantes/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Participant, ActivityType, Activity

@admin.register(Participant)
class ParticipanteAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'cpf', 'phone_number', 'nome_completo_link',)
    search_fields = ('full_name', 'email', 'cpf')
    list_filter = ('full_name', 'email')
    filter_horizontal = ('activities',)

    # Excluindo o campo slug do admin
    exclude = ('slug',)

    def nome_completo_link(self, obj):
        if obj.slug:
            link = reverse('participant_card', args=[obj.slug])
            return format_html('<a href="{}" target="_blank">{}</a>', link, "Imprimir")
        return "Sem link"

    nome_completo_link.short_description = 'Imprimir'

    class Media:
        js = ('etiva/js/admin.js',)  

@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name',)
    search_fields = ('type_name',)
    list_filter = ('type_name',)

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('activity_name', 'activity_date', 'activity_time', 'responsible_person', 'location', 'activity_type_link')
    search_fields = ('activity_name', 'responsible_person', 'location')
    list_filter = ('activity_date', 'activity_type')

    def activity_type_link(self, obj):
        link = reverse('activity_detail', args=[obj.id])  # Usar obj.id ou um campo único
        return format_html('<a href="{}" target="_blank">{}</a>', link, obj.activity_type)

    activity_type_link.short_description = 'Tipo de Atividade'
