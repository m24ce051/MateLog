from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import timedelta
from .models import ActividadPantalla, SesionEstudio
from .serializers import (ActividadPantallaSerializer, IniciarActividadSerializer,
                          FinalizarActividadSerializer)


@method_decorator(csrf_exempt, name='dispatch')
class IniciarActividadView(APIView):
    """
    Vista para iniciar tracking de una pantalla.
    Endpoint: POST /api/tracking/iniciar/
    """
    permission_classes = [AllowAny]  # Permite tracking pre-login
    
    def post(self, request):
        serializer = IniciarActividadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        usuario = request.user if request.user.is_authenticated else None
        
        actividad = ActividadPantalla.objects.create(
            usuario=usuario,
            tipo_pantalla=serializer.validated_data['tipo_pantalla'],
            metadatos=serializer.validated_data.get('metadatos', {})
        )
        
        return Response({
            'actividad_id': actividad.id,
            'timestamp': actividad.timestamp_inicio
        }, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class FinalizarActividadView(APIView):
    """
    Vista para finalizar tracking de una pantalla.
    Endpoint: POST /api/tracking/finalizar/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = FinalizarActividadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        actividad_id = serializer.validated_data['actividad_id']
        
        try:
            actividad = ActividadPantalla.objects.get(id=actividad_id)
            actividad.timestamp_fin = timezone.now()
            actividad.duracion_segundos = int(
                (actividad.timestamp_fin - actividad.timestamp_inicio).total_seconds()
            )
            actividad.save()
            
            return Response({
                'message': 'Actividad finalizada',
                'duracion_segundos': actividad.duracion_segundos
            }, status=status.HTTP_200_OK)
        
        except ActividadPantalla.DoesNotExist:
            return Response({
                'error': 'Actividad no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name='dispatch')
class IniciarSesionView(APIView):
    """
    Vista para iniciar una sesión de estudio.
    Endpoint: POST /api/tracking/sesion/iniciar/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Finalizar sesión anterior si existe
        sesion_activa = SesionEstudio.objects.filter(
            usuario=request.user,
            timestamp_fin__isnull=True
        ).first()
        
        if sesion_activa:
            sesion_activa.timestamp_fin = timezone.now()
            sesion_activa.duracion_minutos = int(
                (sesion_activa.timestamp_fin - sesion_activa.timestamp_inicio).total_seconds() / 60
            )
            sesion_activa.save()
        
        # Crear nueva sesión
        nueva_sesion = SesionEstudio.objects.create(
            usuario=request.user
        )
        
        return Response({
            'sesion_id': nueva_sesion.id,
            'timestamp_inicio': nueva_sesion.timestamp_inicio
        }, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class FinalizarSesionView(APIView):
    """
    Vista para finalizar la sesión de estudio actual.
    Endpoint: POST /api/tracking/sesion/finalizar/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        sesion_activa = SesionEstudio.objects.filter(
            usuario=request.user,
            timestamp_fin__isnull=True
        ).order_by('-timestamp_inicio').first()
        
        if not sesion_activa:
            return Response({
                'error': 'No hay sesión activa'
            }, status=status.HTTP_404_NOT_FOUND)
        
        sesion_activa.timestamp_fin = timezone.now()
        sesion_activa.duracion_minutos = int(
            (sesion_activa.timestamp_fin - sesion_activa.timestamp_inicio).total_seconds() / 60
        )
        sesion_activa.save()
        
        return Response({
            'message': 'Sesión finalizada',
            'duracion_minutos': sesion_activa.duracion_minutos
        }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class VolverContenidoView(APIView):
    """
    Vista para registrar cuando el usuario vuelve al contenido después de ejercicios.
    Endpoint: POST /api/tracking/volver-contenido/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        tema_id = request.data.get('tema_id')
        
        if not tema_id:
            return Response({
                'error': 'tema_id es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Registrar como actividad
        ActividadPantalla.objects.create(
            usuario=request.user,
            tipo_pantalla='VOLVER_CONTENIDO',
            metadatos={'tema_id': tema_id}
        )
        
        return Response({
            'message': 'Acción registrada'
        }, status=status.HTTP_200_OK)