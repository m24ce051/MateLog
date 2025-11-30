from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import SesionEstudio, ActividadPantalla


class IniciarSesionView(APIView):
    """
    Vista para iniciar una sesión de estudio.
    Endpoint: POST /api/tracking/sesion/iniciar/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        sesion = SesionEstudio.objects.create(usuario=request.user)
        return Response({
            'sesion_id': sesion.id,
            'fecha_inicio': sesion.fecha_inicio
        }, status=status.HTTP_201_CREATED)


class FinalizarSesionView(APIView):
    """
    Vista para finalizar una sesión de estudio.
    Endpoint: POST /api/tracking/sesion/finalizar/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        sesion_id = request.data.get('sesion_id')
        
        if not sesion_id:
            return Response(
                {'error': 'Se requiere sesion_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sesion = get_object_or_404(SesionEstudio, id=sesion_id, usuario=request.user)
        sesion.fecha_fin = timezone.now()
        
        # Calcular duración en minutos
        duracion = (sesion.fecha_fin - sesion.fecha_inicio).total_seconds() / 60
        sesion.duracion_minutos = int(duracion)
        sesion.save()
        
        return Response({
            'mensaje': 'Sesión finalizada correctamente',
            'duracion_minutos': sesion.duracion_minutos
        }, status=status.HTTP_200_OK)


class IniciarActividadView(APIView):
    """
    Vista para registrar el inicio de una actividad en una pantalla.
    Endpoint: POST /api/tracking/iniciar/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        tipo_pantalla = request.data.get('tipo_pantalla', 'OTRA')
        
        # Obtener metadatos opcionales
        metadata = request.data.get('metadata', {})
        leccion_id = metadata.get('leccion_id')
        tema_id = metadata.get('tema_id')
        
        # Crear actividad
        actividad = ActividadPantalla.objects.create(
            usuario=request.user if request.user.is_authenticated else None,
            tipo_pantalla=tipo_pantalla,
            leccion_id=leccion_id,
            tema_id=tema_id
        )
        
        return Response({
            'actividad_id': actividad.id,
            'tiempo_inicio': actividad.tiempo_inicio
        }, status=status.HTTP_201_CREATED)


class FinalizarActividadView(APIView):
    """
    Vista para finalizar una actividad de pantalla.
    Endpoint: POST /api/tracking/finalizar/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        actividad_id = request.data.get('actividad_id')
        
        if not actividad_id:
            return Response(
                {'error': 'Se requiere actividad_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            actividad = ActividadPantalla.objects.get(id=actividad_id)
            actividad.tiempo_fin = timezone.now()
            
            # Calcular tiempo en segundos
            tiempo_total = (actividad.tiempo_fin - actividad.tiempo_inicio).total_seconds()
            actividad.tiempo_segundos = int(tiempo_total)
            actividad.save()
            
            return Response({
                'mensaje': 'Actividad finalizada correctamente',
                'tiempo_segundos': actividad.tiempo_segundos
            }, status=status.HTTP_200_OK)
            
        except ActividadPantalla.DoesNotExist:
            return Response(
                {'error': 'Actividad no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )


class RegistrarVolverContenidoView(APIView):
    """
    Vista para registrar cuando el usuario presiona el botón "Volver" en el contenido.
    Endpoint: POST /api/tracking/volver-contenido/
    Modificación 4: Tracking de navegación hacia atrás.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        actividad_id = request.data.get('actividad_id')
        
        if not actividad_id:
            return Response(
                {'error': 'Se requiere actividad_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            actividad = ActividadPantalla.objects.get(id=actividad_id)
            actividad.veces_volver_contenido += 1
            actividad.save()
            
            return Response({
                'mensaje': 'Click en volver registrado',
                'veces_volver': actividad.veces_volver_contenido
            }, status=status.HTTP_200_OK)
            
        except ActividadPantalla.DoesNotExist:
            return Response(
                {'error': 'Actividad no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )