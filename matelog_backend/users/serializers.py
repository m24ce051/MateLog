from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer para login de usuarios.
    """
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        """
        Validar credenciales.
        """
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            # Primero verificar si el usuario existe
            try:
                user_exists = CustomUser.objects.get(username=username)
                print(f"DEBUG: Usuario encontrado: {user_exists.username}")
                print(f"DEBUG: Usuario activo: {user_exists.is_active}")
            except CustomUser.DoesNotExist:
                print(f"DEBUG: Usuario '{username}' NO existe en la base de datos")
                raise serializers.ValidationError({
                    'username': f'El usuario "{username}" no existe.'
                })
            
            # Intentar autenticar
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            print(f"DEBUG: Resultado de authenticate(): {user}")
            
            if not user:
                # Verificar si el problema es la contraseña
                print(f"DEBUG: Autenticación falló para usuario '{username}'")
                raise serializers.ValidationError({
                    'password': 'Contraseña incorrecta.'
                })
            
            if not user.is_active:
                raise serializers.ValidationError({
                    'username': 'Esta cuenta ha sido desactivada.'
                })
            
            data['user'] = user
        else:
            raise serializers.ValidationError(
                'Debe proporcionar usuario y contraseña.'
            )
        
        return data