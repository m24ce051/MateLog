from rest_framework import serializers
from .models import Leccion, Tema, ContenidoTema, Ejercicio, OpcionMultiple


class OpcionMultipleSerializer(serializers.ModelSerializer):
    """
    Serializer para opciones múltiples.
    """
    class Meta:
        model = OpcionMultiple
        fields = ['letra', 'texto']


class ContenidoTemaSerializer(serializers.ModelSerializer):
    """
    Serializer para contenido de temas (teoría/ejemplos).
    Las imágenes están incrustadas en contenido_texto mediante TinyMCE.
    """
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = ContenidoTema
        fields = ['id', 'tipo', 'tipo_display', 'orden', 'contenido_texto']


class EjercicioSerializer(serializers.ModelSerializer):
    """
    Serializer para ejercicios (sin incluir la respuesta correcta).
    Las imágenes están incrustadas en enunciado mediante TinyMCE.
    """
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    dificultad_display = serializers.CharField(source='get_dificultad_display', read_only=True)
    opciones = OpcionMultipleSerializer(many=True, read_only=True)
    tiene_ayuda = serializers.SerializerMethodField()
    
    class Meta:
        model = Ejercicio
        fields = ['id', 'orden', 'tipo', 'tipo_display', 'dificultad', 
                 'dificultad_display', 'mostrar_dificultad', 'instruccion', 
                 'enunciado', 'opciones', 'texto_ayuda', 'tiene_ayuda']
    
    def get_tiene_ayuda(self, obj):
        return bool(obj.texto_ayuda)


class EjercicioValidacionSerializer(serializers.Serializer):
    """
    Serializer para validar respuestas de ejercicios.
    """
    ejercicio_id = serializers.IntegerField()
    respuesta = serializers.CharField(max_length=500)
    uso_ayuda = serializers.BooleanField(default=False)
    tiempo_respuesta_segundos = serializers.IntegerField(required=False, allow_null=True)


class TemaListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para lista de temas.
    """
    cantidad_contenidos = serializers.SerializerMethodField()
    cantidad_ejercicios = serializers.SerializerMethodField()
    
    class Meta:
        model = Tema
        fields = ['id', 'titulo', 'descripcion', 'orden', 
                 'cantidad_contenidos', 'cantidad_ejercicios']
    
    def get_cantidad_contenidos(self, obj):
        return obj.contenidos.count()
    
    def get_cantidad_ejercicios(self, obj):
        return obj.ejercicios.count()


class TemaDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para un tema específico con su contenido.
    """
    contenidos = ContenidoTemaSerializer(many=True, read_only=True)
    ejercicios = EjercicioSerializer(many=True, read_only=True)
    
    class Meta:
        model = Tema
        fields = ['id', 'titulo', 'descripcion', 'orden', 'contenidos', 'ejercicios']


class LeccionListSerializer(serializers.ModelSerializer):
    """
    Serializer para lista de lecciones (solo activas).
    """
    cantidad_temas = serializers.SerializerMethodField()
    
    class Meta:
        model = Leccion
        fields = ['id', 'titulo', 'descripcion', 'orden', 'cantidad_temas']
    
    def get_cantidad_temas(self, obj):
        return obj.temas.filter(is_active=True).count()


class LeccionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para una lección con sus temas.
    """
    temas = TemaListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Leccion
        fields = ['id', 'titulo', 'descripcion', 'orden', 'temas']
    
    def get_temas(self, obj):
        return obj.temas.filter(is_active=True)