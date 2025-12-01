from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de nuevos usuarios.
    """
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 
            'email', 
            'password', 
            'grupo', 
            'especialidad', 
            'genero', 
            'edad'
        ]
    
    def create(self, validated_data):
        """
        Crear usuario con contraseña hasheada.
        """
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer para login de usuarios con DEBUG.
    """
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        """
        Validar credenciales con DEBUG mejorado.
        """
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            # DEBUG: Verificar si el usuario existe
            try:
                user_exists = CustomUser.objects.get(username=username)
                print(f"✅ DEBUG: Usuario encontrado: {user_exists.username}")
                print(f"✅ DEBUG: Usuario activo: {user_exists.is_active}")
                print(f"✅ DEBUG: Password hash: {user_exists.password[:50]}...")
                print(f"✅ DEBUG: Grupo: {user_exists.grupo}")
                print(f"✅ DEBUG: Edad: {user_exists.edad}")
            except CustomUser.DoesNotExist:
                print(f"❌ DEBUG: Usuario '{username}' NO existe en la base de datos")
                raise serializers.ValidationError({
                    'username': f'El usuario "{username}" no existe.'
                })
            
            # Intentar autenticar
            print(f"🔐 DEBUG: Intentando authenticate() para '{username}'...")
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            print(f"🔐 DEBUG: Resultado de authenticate(): {user}")
            
            if not user:
                print(f"❌ DEBUG: authenticate() FALLÓ para '{username}'")
                print(f"❌ DEBUG: La contraseña proporcionada NO coincide con el hash")
                raise serializers.ValidationError({
                    'password': 'Contraseña incorrecta.'
                })
            
            if not user.is_active:
                raise serializers.ValidationError({
                    'username': 'Esta cuenta ha sido desactivada.'
                })
            
            print(f"✅ DEBUG: Autenticación EXITOSA para '{username}'")
            data['user'] = user
        else:
            raise serializers.ValidationError(
                'Debe proporcionar usuario y contraseña.'
            )
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para perfil de usuario.
    """
    class Meta:
        model = CustomUser
        fields = [
            'id', 
            'username', 
            'email', 
            'grupo', 
            'especialidad', 
            'genero', 
            'edad',
            'fecha_registro',
            'ultima_actividad'
        ]
        read_only_fields = ['id', 'username', 'fecha_registro', 'ultima_actividad']


class ChoicesSerializer(serializers.Serializer):
    """
    Serializer para opciones de registro.
    """
    grupo_choices = serializers.SerializerMethodField()
    especialidad_choices = serializers.SerializerMethodField()
    genero_choices = serializers.SerializerMethodField()
    edad_choices = serializers.SerializerMethodField()
    
    def get_grupo_choices(self, obj):
        return [{'value': k, 'label': v} for k, v in CustomUser.GRUPO_CHOICES]
    
    def get_especialidad_choices(self, obj):
        return [{'value': k, 'label': v} for k, v in CustomUser.ESPECIALIDAD_CHOICES]
    
    def get_genero_choices(self, obj):
        return [{'value': k, 'label': v} for k, v in CustomUser.GENDER_CHOICES]
    
    def get_edad_choices(self, obj):
        return [{'value': k, 'label': v} for k, v in CustomUser.EDAD_CHOICES]