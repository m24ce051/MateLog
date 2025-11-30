from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.http import JsonResponse
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, ChoicesSerializer


class RegisterView(APIView):
    """
    Vista para registro de nuevos usuarios.
    Endpoint: POST /api/users/register/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'mensaje': 'Usuario registrado exitosamente',
                'usuario': {
                    'id': user.id,
                    'username': user.username,
                    'grupo': user.grupo,
                    'especialidad': user.especialidad,
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Vista para inicio de sesión.
    Endpoint: POST /api/users/login/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return Response({
                    'mensaje': 'Inicio de sesión exitoso',
                    'usuario': {
                        'id': user.id,
                        'username': user.username,
                        'grupo': user.grupo,
                        'especialidad': user.especialidad,
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Credenciales inválidas'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Vista para cerrar sesión.
    Endpoint: POST /api/users/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({
            'mensaje': 'Sesión cerrada exitosamente'
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    Vista para obtener información del perfil del usuario autenticado.
    Endpoint: GET /api/users/profile/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegistrationChoicesView(APIView):
    """
    Vista para obtener las opciones disponibles para los campos del formulario de registro.
    Endpoint: GET /api/users/choices/
    No requiere autenticación.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        serializer = ChoicesSerializer()
        return Response(serializer.to_representation(None), status=status.HTTP_200_OK)


class CSRFTokenView(APIView):
    """
    Vista para obtener el CSRF token.
    Endpoint: GET /api/users/csrf/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        csrf_token = get_token(request)
        return JsonResponse({'csrfToken': csrf_token})