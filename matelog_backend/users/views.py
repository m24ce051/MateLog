from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .serializers import (UserRegistrationSerializer, UserLoginSerializer, 
                          UserProfileSerializer, ChoicesSerializer)


@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationView(APIView):
    """
    Vista para registro de nuevos usuarios.
    Endpoint: POST /api/users/register/
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Sin autenticación
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Usuario registrado exitosamente',
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(APIView):
    """
    Vista para login de usuarios.
    Endpoint: POST /api/users/login/
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Sin autenticación
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data.get('user') or serializer.validated_data.get('usuario')
            
            if not user:
                return Response({
                    'error': 'Error en autenticación'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Iniciar sesión
            login(request, user)
            
            return Response({
                'message': 'Login exitoso',
                'usuario': UserProfileSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class UserLogoutView(APIView):
    """
    Vista para logout de usuarios.
    Endpoint: POST /api/users/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({
            'message': 'Logout exitoso'
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    Vista para obtener/actualizar perfil de usuario.
    Endpoint: GET/PUT /api/users/profile/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserProfileSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrationChoicesView(APIView):
    """
    Vista para obtener las opciones de registro.
    Endpoint: GET /api/users/choices/
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Sin autenticación
    
    def get(self, request):
        serializer = ChoicesSerializer(data={})
        serializer.is_valid()
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class GetCSRFToken(APIView):
    """
    Vista para obtener CSRF token (ya no necesaria pero la dejamos por compatibilidad).
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Sin autenticación
    
    def get(self, request):
        return Response({'detail': 'CSRF disabled'})