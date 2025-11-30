from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import (UserRegistrationSerializer, UserLoginSerializer, 
                          UserProfileSerializer, ChoicesSerializer)


@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationView(APIView):
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
    
    def post(self, request):
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            
            return Response({
                'message': 'Inicio de sesión exitoso',
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


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
            'message': 'Sesión cerrada exitosamente'
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    Vista para obtener el perfil del usuario autenticado.
    Endpoint: GET /api/users/profile/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetChoicesView(APIView):
    """
    Vista para obtener choices de registro (grupos, especialidades, etc).
    Endpoint: GET /api/users/choices/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        serializer = ChoicesSerializer()
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetCSRFTokenView(APIView):
    """
    Vista para obtener CSRF token.
    Endpoint: GET /api/users/csrf/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        from django.middleware.csrf import get_token
        return Response({
            'csrfToken': get_token(request)
        }, status=status.HTTP_200_OK)