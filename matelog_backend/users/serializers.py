from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para el registro de nuevos usuarios.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'password_confirm', 'grupo', 'especialidad', 'genero', 'edad')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "Las contraseñas no coinciden."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer para el inicio de sesión.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar el perfil del usuario.
    Incluye los valores display de los campos con choices.
    """
    grupo_display = serializers.CharField(source='get_grupo_display', read_only=True)
    especialidad_display = serializers.CharField(source='get_especialidad_display', read_only=True)
    genero_display = serializers.CharField(source='get_genero_display', read_only=True)
    edad_display = serializers.CharField(source='get_edad_display', read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'id', 
            'username', 
            'grupo', 
            'grupo_display',
            'especialidad', 
            'especialidad_display',
            'genero',
            'genero_display',
            'edad',
            'edad_display',
            'date_joined'
        )


class ChoicesSerializer(serializers.Serializer):
    """
    Serializer para exponer las opciones de choices en la API.
    Permite que el frontend cargue dinámicamente las opciones de los dropdowns.
    """
    def to_representation(self, instance):
        from users.models import GRUPO_CHOICES, ESPECIALIDAD_CHOICES, GENERO_CHOICES, EDAD_CHOICES
        
        return {
            'grupos': [{'value': value, 'label': label} for value, label in GRUPO_CHOICES],
            'especialidades': [{'value': value, 'label': label} for value, label in ESPECIALIDAD_CHOICES],
            'generos': [{'value': value, 'label': label} for value, label in GENERO_CHOICES],
            'edades': [{'value': value, 'label': label} for value, label in EDAD_CHOICES],
        }