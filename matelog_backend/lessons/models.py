from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import unicodedata


class Leccion(models.Model):
    """
    Modelo de Lección. Representa el nivel superior de contenido.
    Usa soft delete (is_active) para mantener IDs consistentes.
    """
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(
        help_text="Descripción de la lección (soporta HTML desde TinyMCE)"
    )
    orden = models.PositiveIntegerField(unique=True, 
                                       help_text="Orden de aparición en el frontend")
    is_active = models.BooleanField(default=True, 
                                    verbose_name="Activa",
                                    help_text="Si está inactiva, no se mostrará en el frontend")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Lección'
        verbose_name_plural = 'Lecciones'
        ordering = ['orden']
    
    def __str__(self):
        status = "✓" if self.is_active else "✗"
        return f"{status} Lección {self.orden}: {self.titulo}"


class Tema(models.Model):
    """
    Modelo de Tema. Pertenece a una Lección.
    Contiene la teoría/ejemplos y los ejercicios.
    """
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE, 
                               related_name='temas')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(
        help_text="Descripción del tema (soporta HTML desde TinyMCE)"
    )
    orden = models.PositiveIntegerField(
        help_text="Orden dentro de la lección"
    )
    is_active = models.BooleanField(default=True, 
                                    verbose_name="Activo",
                                    help_text="Si está inactivo, no se mostrará en el frontend")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tema'
        verbose_name_plural = 'Temas'
        ordering = ['leccion__orden', 'orden']
        unique_together = ['leccion', 'orden']
    
    def __str__(self):
        status = "✓" if self.is_active else "✗"
        return f"{status} {self.leccion.titulo} - Tema {self.orden}: {self.titulo}"


class ContenidoTema(models.Model):
    """
    Modelo para los recuadros de Teoría, Ejemplo y Ejemplo Extra.
    Se muestran secuencialmente antes de los ejercicios.
    Las imágenes se insertan mediante TinyMCE.
    """
    TIPO_CHOICES = [
        ('TEORIA', 'Teoría'),
        ('EJEMPLO', 'Ejemplo'),
        ('EJEMPLO_EXTRA', 'Ejemplo Extra'),
    ]
    
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, 
                            related_name='contenidos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    orden = models.PositiveIntegerField(
        help_text="Orden de aparición dentro del tema"
    )
    
    # Contenido con HTML desde TinyMCE (incluye imágenes incrustadas)
    contenido_texto = models.TextField(
        help_text="Contenido en HTML desde TinyMCE (incluye formato, imágenes, tablas, etc.)"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Contenido de Tema'
        verbose_name_plural = 'Contenidos de Temas'
        ordering = ['tema', 'orden']
        unique_together = ['tema', 'orden']
    
    def __str__(self):
        return f"{self.tema.titulo} - {self.get_tipo_display()} #{self.orden}"


class Ejercicio(models.Model):
    """
    Modelo de Ejercicio. Pertenece a un Tema.
    Puede ser de respuesta abierta o de opción múltiple.
    Las imágenes se insertan mediante TinyMCE en el enunciado.
    """
    TIPO_CHOICES = [
        ('ABIERTO', 'Respuesta Abierta'),
        ('MULTIPLE', 'Opción Múltiple'),
    ]
    
    DIFICULTAD_CHOICES = [
        ('FACIL', 'Fácil'),
        ('INTERMEDIO', 'Intermedio'),
        ('DIFICIL', 'Difícil'),
    ]
    
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, 
                            related_name='ejercicios')
    orden = models.PositiveIntegerField(
        help_text="Orden dentro del tema (número de ejercicio)"
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    dificultad = models.CharField(max_length=15, choices=DIFICULTAD_CHOICES)
    
    # Contenido del ejercicio
    instruccion = models.TextField(
        help_text="Instrucciones para el estudiante (soporta HTML desde TinyMCE)"
    )
    enunciado = models.TextField(
        verbose_name="Ejercicio",
        help_text="El ejercicio en sí (soporta HTML desde TinyMCE, incluye imágenes)"
    )
    
    # Respuesta correcta
    respuesta_correcta = models.CharField(max_length=500,
        help_text="Para abiertos: respuesta exacta. Para múltiple: letra de opción correcta (A, B, C, D)"
    )
    
    # Texto de ayuda y retroalimentación
    texto_ayuda = models.TextField(
        blank=True,
        help_text="Texto que se muestra al presionar 'Ayuda' (soporta HTML desde TinyMCE)"
    )
    retroalimentacion_correcta = models.TextField(
        blank=True,
        verbose_name="Retroalimentación (correcta)",
        help_text="Mensaje cuando la respuesta es correcta (soporta HTML desde TinyMCE)"
    )
    retroalimentacion_incorrecta = models.TextField(
        blank=True,
        verbose_name="Retroalimentación (incorrecta)",
        help_text="Mensaje cuando la respuesta es incorrecta (soporta HTML desde TinyMCE)"
    )
    
    # Control de visualización
    mostrar_dificultad = models.BooleanField(
        default=False,
        verbose_name="Mostrar dificultad",
        help_text="Si se marca, la dificultad será visible para el estudiante"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ejercicio'
        verbose_name_plural = 'Ejercicios'
        ordering = ['tema', 'orden']
        unique_together = ['tema', 'orden']
    
    def __str__(self):
        return f"{self.tema.titulo} - Ejercicio {self.orden}"
    
    def validar_respuesta(self, respuesta_usuario):
        """
        Valida la respuesta del usuario.
        Para abiertos: ignora mayúsculas, espacios y tildes.
        Para múltiple: compara directamente.
        """
        if self.tipo == 'MULTIPLE':
            return respuesta_usuario.strip().upper() == self.respuesta_correcta.upper()
        
        # Para respuestas abiertas: normalizar
        def normalizar(texto):
            # Quitar espacios extras
            texto = ' '.join(texto.split())
            # Convertir a minúsculas
            texto = texto.lower()
            # Quitar tildes
            texto = ''.join(
                c for c in unicodedata.normalize('NFD', texto)
                if unicodedata.category(c) != 'Mn'
            )
            return texto
        
        return normalizar(respuesta_usuario) == normalizar(self.respuesta_correcta)


class OpcionMultiple(models.Model):
    """
    Opciones para ejercicios de opción múltiple.
    Máximo 4 opciones (A, B, C, D).
    """
    LETRA_CHOICES = [
        ('A', 'Opción A'),
        ('B', 'Opción B'),
        ('C', 'Opción C'),
        ('D', 'Opción D'),
    ]
    
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE,
                                 related_name='opciones',
                                 limit_choices_to={'tipo': 'MULTIPLE'})
    letra = models.CharField(max_length=1, choices=LETRA_CHOICES)
    texto = models.CharField(max_length=500,
                            help_text="Texto de la opción")
    
    class Meta:
        verbose_name = 'Opción Múltiple'
        verbose_name_plural = 'Opciones Múltiples'
        ordering = ['ejercicio', 'letra']
        unique_together = ['ejercicio', 'letra']
    
    def __str__(self):
        return f"{self.ejercicio} - Opción {self.letra}"