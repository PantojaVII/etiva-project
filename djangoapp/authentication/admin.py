from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'auth_method', 'is_active', 'is_staff', 'is_superuser', 'id')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'auth_method')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'auth_method')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('last_login', 'created_at', 'updated_at')
    search_fields = ('email', 'username')
    ordering = ('email',)
    filter_horizontal = ()

#@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Campos que serão exibidos na listagem de perfis
    list_display = ('id', 'user', 'first_name', 'last_name', 'phone_number', 'date_of_birth')
    
    # Campos que poderão ser pesquisados no admin
    search_fields = ('user__username', 'first_name', 'last_name', 'phone_number')
    
    # Campos que poderão ser filtrados na listagem
    list_filter = ('date_of_birth',)

    # Campos editáveis diretamente na listagem (opcional)
    list_editable = ('first_name', 'last_name', 'phone_number')