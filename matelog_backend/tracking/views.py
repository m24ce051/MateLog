from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import ActividadPantalla, SesionEstudio, VolverContenido
from .serializers import (
    ActividadPantallaSerializer,
    SesionEstudioSerializer,
    VolverContenidoSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class IniciarActividadView(APIView):
    """
    Vista para iniciar tracking de una pantalla.
    Endpoint: POST /api/tracking/iniciar/
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Sin autenticación
    
    def post(self, request):
        try:
            # Si el usuario no está autenticado, devolver respuesta exitosa sin crear registro
            if not request.user.is_authenticated:
                return Response({
                    'actividad_id': None,
                    'timestamp': timezone.now(),
                    'message': 'Tracking skipped for anonymous user'
                }, status=status.HTTP_201_CREATED)
            
            serializer = ActividadPantallaSerializer(data=request.data)
            
            if serializer.is_valid():
                usuario = request.user
                
                actividad = ActividadPantalla.objects.create(
                    usuario=usuario,
                    tipo_pantalla=serializer.validated_data['tipo_pantalla']
                )
                
                return Response({
                    'actividad_id': actividad.id,
                    'timestamp': actividad.timestamp_inicio
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': f'Error al iniciar actividad: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class FinalizarActividadView(APIView):
    """
    Vista para finalizar tracking de una pantalla.
    Endpoint: POST /api/tracking/finalizar/
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Sin autenticación
    
    def post(self, request):
        try:
            actividad_id = request.data.get('actividad_id')
            
            # Si no hay actividad_id (usuario anónimo), devolver respuesta exitosa
            if actividad_id is None:
                return Response({
                    'message': 'Tracking skipped for anonymous user',
                    'duracion_segundos': 0
                }, status=status.HTTP_200_OK)
            
            actividad = ActividadPantalla.objects.get(id=actividad_id)
            actividad.timestamp_fin = timezone.now()
            actividad.duracion_segundos = (
                actividad.timestamp_fin - actividad.timestamp_inicio
            ).total_seconds()
            actividad.save()
            
            return Response({
                'message': 'Actividad finalizada',
                'duracion_segundos': actividad.duracion_segundos
            }, status=status.HTTP_200_OK)
            
        except ActividadPantalla.DoesNotExist:
            return Response({
                'error': 'Actividad no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Error al finalizar actividad: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class IniciarSesionView(APIView):
    """
    Vista para iniciar una sesión de estudio.
    Endpoint: POST /api/tracking/sesion/iniciar/
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Sin autenticación
    
    def post(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({
                    'error': 'Usuario no autenticado'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            serializer = SesionEstudioSerializer(data=request.data)
            
            if serializer.is_valid():
                sesion = SesionEstudio.objects.create(
                    usuario=request.user,
                    leccion=serializer.validated_data.get('leccion')
                )
                
                return Response({
                    'sesion_id': sesion.id,
                    'timestamp': sesion.inicio
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': f'Error al iniciar sesión: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class FinalizarSesionView(APIView):
    """
    Vista para finalizar una sesión de estudio.
    Endpoint: POST /api/tracking/sesion/finalizar/
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Sin autenticación
    
    def post(self, request):
        try:
            sesion_id = request.data.get('sesion_id')
            
            sesion = SesionEstudio.objects.get(id=sesion_id)
            sesion.fin = timezone.now()
            sesion.duracion_minutos = (
                sesion.fin - sesion.inicio
            ).total_seconds() / 60
            sesion.save()
            
            return Response({
                'message': 'Sesión finalizada',
                'duracion_minutos': sesion.duracion_minutos
            }, status=status.HTTP_200_OK)
            
        except SesionEstudio.DoesNotExist:
            return Response({
                'error': 'Sesión no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Error al finalizar sesión: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class VolverContenidoView(APIView):
    """
    Vista para registrar cuando un usuario vuelve a ver contenido.
    Endpoint: POST /api/tracking/volver/
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Sin autenticación
    
    def post(self, request):
        try:
            if not request.user.is_authenticated:
                return Response({
                    'error': 'Usuario no autenticado'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            serializer = VolverContenidoSerializer(data=request.data)
            
            if serializer.is_valid():
                volver = VolverContenido.objects.create(
                    usuario=request.user,
                    leccion=serializer.validated_data['leccion'],
                    motivo=serializer.validated_data.get('motivo', '')
                )
                
                return Response({
                    'message': 'Registro de volver a contenido creado',
                    'id': volver.id
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': f'Error al registrar volver: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)