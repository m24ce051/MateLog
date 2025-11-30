from django.db import models
from django.conf import settings
from lessons.models import Leccion, Tema, Ejercicio


class SesionEstudio(models.Model):
    """
    Modelo para registrar las sesiones de estudio de los usuarios.
    Una sesión abarca desde que el usuario inicia sesión hasta que cierra.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sesiones'
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    duracion_minutos = models.IntegerField(
        default=0,
        help_text="Duración total de la sesión en minutos"
    )

    class Meta:
        verbose_name = 'Sesión de Estudio'
        verbose_name_plural = 'Sesiones de Estudio'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha_inicio.strftime('%Y-%m-%d %H:%M')}"


class ProgresoLeccion(models.Model):
    """
    Modelo para registrar el progreso del usuario en cada lección.
    """
    ESTADO_CHOICES = [
        ('SIN_INICIAR', 'Sin Iniciar'),
        ('EN_PROGRESO', 'En Progreso'),
        ('COMPLETADA', 'Completada'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progreso_lecciones'
    )
    leccion = models.ForeignKey(
        Leccion,
        on_delete=models.CASCADE,
        related_name='progreso_usuarios'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='SIN_INICIAR'
    )
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    porcentaje_completado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Porcentaje de temas completados en la lección"
    )

    class Meta:
        verbose_name = 'Progreso de Lección'
        verbose_name_plural = 'Progreso de Lecciones'
        unique_together = ['usuario', 'leccion']
        ordering = ['leccion__orden']

    def __str__(self):
        return f"{self.usuario.username} - {self.leccion.titulo} ({self.estado})"


class ProgresoTema(models.Model):
    """
    Modelo para registrar el progreso del usuario en cada tema.
    """
    ESTADO_CHOICES = [
        ('SIN_INICIAR', 'Sin Iniciar'),
        ('INICIADO', 'Iniciado'),
        ('COMPLETADO', 'Completado'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progreso_temas'
    )
    tema = models.ForeignKey(
        Tema,
        on_delete=models.CASCADE,
        related_name='progreso_usuarios'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='SIN_INICIAR'
    )
    desbloqueado = models.BooleanField(
        default=False,
        help_text="Indica si el tema está desbloqueado para el usuario"
    )
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    porcentaje_acierto = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Porcentaje de aciertos en los ejercicios del tema"
    )
    intentos_realizados = models.PositiveIntegerField(
        default=0,
        help_text="Número de veces que el usuario ha intentado completar este tema"
    )

    class Meta:
        verbose_name = 'Progreso de Tema'
        verbose_name_plural = 'Progreso de Temas'
        unique_together = ['usuario', 'tema']
        ordering = ['tema__orden']

    def __str__(self):
        return f"{self.usuario.username} - {self.tema.titulo} ({self.estado})"


class RespuestaEjercicio(models.Model):
    """
    Modelo para registrar las respuestas de los usuarios a los ejercicios.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='respuestas'
    )
    ejercicio = models.ForeignKey(
        Ejercicio,
        on_delete=models.CASCADE,
        related_name='respuestas_usuarios'
    )
    progreso_tema = models.ForeignKey(
        ProgresoTema,
        on_delete=models.CASCADE,
        related_name='respuestas',
        null=True,
        blank=True
    )
    respuesta_usuario = models.TextField(help_text="Respuesta proporcionada por el usuario")
    es_correcta = models.BooleanField(help_text="Indica si la respuesta fue correcta")
    uso_ayuda = models.BooleanField(
        default=False,
        help_text="Indica si el usuario vio la ayuda antes de responder"
    )
    tiempo_respuesta_segundos = models.IntegerField(
        default=0,
        help_text="Tiempo que tardó el usuario en responder (en segundos)"
    )
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Respuesta de Ejercicio'
        verbose_name_plural = 'Respuestas de Ejercicios'
        ordering = ['-fecha_respuesta']

    def __str__(self):
        return f"{self.usuario.username} - {self.ejercicio.enunciado[:50]} - {'Correcta' if self.es_correcta else 'Incorrecta'}"


class ActividadPantalla(models.Model):
    """
    Modelo para registrar el tiempo que el usuario pasa en cada pantalla.
    """
    TIPO_PANTALLA_CHOICES = [
        ('LOGIN', 'Login'),
        ('REGISTRO', 'Registro'),
        ('LISTA_LECCIONES', 'Lista de Lecciones'),
        ('DETALLE_LECCION', 'Detalle de Lección'),
        ('CONTENIDO_TEMA', 'Contenido del Tema'),
        ('EJERCICIOS', 'Ejercicios'),
        ('OTRA', 'Otra'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='actividades_pantalla',
        null=True,
        blank=True
    )
    tipo_pantalla = models.CharField(
        max_length=30,
        choices=TIPO_PANTALLA_CHOICES
    )
    tiempo_inicio = models.DateTimeField(auto_now_add=True)
    tiempo_fin = models.DateTimeField(null=True, blank=True)
    tiempo_segundos = models.IntegerField(
        default=0,
        help_text="Tiempo total en la pantalla en segundos"
    )
    
    # Metadatos adicionales
    leccion_id = models.IntegerField(null=True, blank=True)
    tema_id = models.IntegerField(null=True, blank=True)
    
    # Modificación 4: Tracking de navegación
    veces_volver_contenido = models.PositiveIntegerField(
        default=0,
        help_text="Número de veces que presionó el botón 'Volver' en el contenido del tema"
    )

    class Meta:
        verbose_name = 'Actividad de Pantalla'
        verbose_name_plural = 'Actividades de Pantalla'
        ordering = ['-tiempo_inicio']

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Anónimo"
        return f"{usuario_str} - {self.tipo_pantalla} - {self.tiempo_segundos}s"


# Modificación 7: Nuevo modelo para tracking de reintentos
class IntentoTema(models.Model):
    """
    Modelo para registrar cada intento que hace un usuario en un tema.
    Permite analizar el progreso y mejora del estudiante en reintentos.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='intentos_temas'
    )
    tema = models.ForeignKey(
        Tema,
        on_delete=models.CASCADE,
        related_name='intentos'
    )
    progreso_tema = models.ForeignKey(
        ProgresoTema,
        on_delete=models.CASCADE,
        related_name='intentos',
        help_text="Relación con el progreso general del tema"
    )
    numero_intento = models.PositiveIntegerField(
        help_text="Número de intento (1, 2, 3, ...)"
    )
    
    # Resultados del intento
    ejercicios_correctos = models.PositiveIntegerField(
        default=0,
        help_text="Cantidad de ejercicios respondidos correctamente"
    )
    ejercicios_incorrectos = models.PositiveIntegerField(
        default=0,
        help_text="Cantidad de ejercicios respondidos incorrectamente"
    )
    ejercicios_totales = models.PositiveIntegerField(
        help_text="Total de ejercicios del tema"
    )
    porcentaje_acierto = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Porcentaje de aciertos en este intento"
    )
    
    # Uso de ayuda
    ejercicios_con_ayuda = models.PositiveIntegerField(
        default=0,
        help_text="Cantidad de ejercicios donde usó la ayuda"
    )
    
    # Tiempos
    tiempo_total_segundos = models.IntegerField(
        default=0,
        help_text="Tiempo total invertido en este intento"
    )
    tiempo_promedio_por_ejercicio = models.IntegerField(
        default=0,
        help_text="Tiempo promedio por ejercicio en segundos"
    )
    
    # Resultado final
    aprobado = models.BooleanField(
        default=False,
        help_text="Indica si alcanzó el 80% requerido para aprobar"
    )
    
    # Fechas
    fecha_inicio = models.DateTimeField(
        help_text="Fecha y hora en que comenzó el intento"
    )
    fecha_finalizacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que finalizó el intento"
    )
    
    # Mejora respecto al intento anterior
    mejora_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Mejora en porcentaje respecto al intento anterior"
    )

    class Meta:
        verbose_name = 'Intento de Tema'
        verbose_name_plural = 'Intentos de Temas'
        ordering = ['-fecha_finalizacion']
        unique_together = ['usuario', 'tema', 'numero_intento']

    def __str__(self):
        return f"{self.usuario.username} - {self.tema.titulo} - Intento {self.numero_intento} ({self.porcentaje_acierto}%)"
    
    def calcular_mejora(self):
        """
        Calcula la mejora respecto al intento anterior.
        """
        if self.numero_intento > 1:
            intento_anterior = IntentoTema.objects.filter(
                usuario=self.usuario,
                tema=self.tema,
                numero_intento=self.numero_intento - 1
            ).first()
            
            if intento_anterior:
                self.mejora_porcentaje = self.porcentaje_acierto - intento_anterior.porcentaje_acierto
            else:
                self.mejora_porcentaje = 0
        else:
            self.mejora_porcentaje = 0