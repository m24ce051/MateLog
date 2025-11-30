from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Configuración del admin para CustomUser.
    """
    # Campos a mostrar en la lista
    list_display = (
        'username',
        'grupo',
        'especialidad',
        'genero',
        'edad',
        'is_active',
        'date_joined',
    )
    
    # Filtros en la barra lateral
    list_filter = (
        'is_active',
        'is_staff',
        'grupo',
        'especialidad',
        'genero',
        'edad',
        'date_joined',
    )
    
    # Campos de búsqueda
    search_fields = ('username', 'first_name', 'last_name')
    
    # Ordenamiento por defecto
    ordering = ('-date_joined',)
    
    # Campos de solo lectura
    readonly_fields = ('date_joined', 'last_login')
    
    # Organización de campos en el formulario de edición
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Información del Estudiante', {
            'fields': ('grupo', 'especialidad', 'genero', 'edad')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas Importantes', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    # Organización de campos en el formulario de creación
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')
        }),
        ('Información del Estudiante', {
            'fields': ('grupo', 'especialidad', 'genero', 'edad')
        }),
    )