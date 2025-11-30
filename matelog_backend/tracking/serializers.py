from rest_framework import serializers
from .models import ProgresoLeccion, ProgresoTema, RespuestaEjercicio, ActividadPantalla


class ProgresoLeccionSerializer(serializers.ModelSerializer):
    """
    Serializer para progreso de lecciones.
    """
    leccion_titulo = serializers.CharField(source='leccion.titulo', read_only=True)
    leccion_orden = serializers.IntegerField(source='leccion.orden', read_only=True)
    
    class Meta:
        model = ProgresoLeccion
        fields = ['id', 'leccion', 'leccion_titulo', 'leccion_orden',
                 'iniciada', 'completada', 'porcentaje_completado',
                 'fecha_inicio', 'fecha_completado']


class ProgresoTemaSerializer(serializers.ModelSerializer):
    """
    Serializer para progreso de temas.
    """
    tema_titulo = serializers.CharField(source='tema.titulo', read_only=True)
    tema_orden = serializers.IntegerField(source='tema.orden', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = ProgresoTema
        fields = ['id', 'tema', 'tema_titulo', 'tema_orden', 'estado', 
                 'estado_display', 'desbloqueado', 'ejercicios_intentados',
                 'ejercicios_correctos', 'ejercicios_incorrectos', 
                 'porcentaje_acierto', 'volvio_de_ejercicios_a_tema']


class RespuestaEjercicioSerializer(serializers.ModelSerializer):
    """
    Serializer para respuestas de ejercicios.
    """
    ejercicio_titulo = serializers.CharField(
        source='ejercicio.tema.titulo', read_only=True
    )
    
    class Meta:
        model = RespuestaEjercicio
        fields = ['id', 'ejercicio', 'ejercicio_titulo', 'respuesta_usuario',
                 'es_correcta', 'uso_ayuda', 'tiempo_respuesta_segundos',
                 'fecha_respuesta']


class ActividadPantallaSerializer(serializers.ModelSerializer):
    """
    Serializer para actividad en pantallas.
    """
    tipo_pantalla_display = serializers.CharField(
        source='get_tipo_pantalla_display', read_only=True
    )
    
    class Meta:
        model = ActividadPantalla
        fields = ['id', 'tipo_pantalla', 'tipo_pantalla_display', 
                 'leccion', 'tema', 'ejercicio', 'timestamp_entrada',
                 'timestamp_salida', 'tiempo_segundos', 'veces_volver_contenido',
                 'detalles_extra']
        read_only_fields = ['timestamp_entrada']


class IniciarActividadSerializer(serializers.Serializer):
    """
    Serializer para iniciar tracking de una pantalla.
    """
    tipo_pantalla = serializers.ChoiceField(choices=ActividadPantalla.TIPO_PANTALLA_CHOICES)
    leccion_id = serializers.IntegerField(required=False, allow_null=True)
    tema_id = serializers.IntegerField(required=False, allow_null=True)
    ejercicio_id = serializers.IntegerField(required=False, allow_null=True)
    detalles_extra = serializers.JSONField(required=False, allow_null=True)


class FinalizarActividadSerializer(serializers.Serializer):
    """
    Serializer para finalizar tracking de una pantalla.
    """
    actividad_id = serializers.IntegerField()