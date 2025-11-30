from django.contrib.auth.models import AbstractUser
from django.db import models

# Choices para campos de registro
GRUPO_CHOICES = [
    ('A', 'Grupo A'),
    ('B', 'Grupo B'),
    ('C', 'Grupo C'),
    ('D', 'Grupo D'),
]

ESPECIALIDAD_CHOICES = [
    ('INFORMATICA', 'Informática'),
    ('AGRONOMIA', 'Agronomía'),
    ('ADMINISTRACION', 'Administración'),
    ('ELECTRONICA', 'Electrónica'),
]

GENERO_CHOICES = [
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('O', 'Otro'),
    ('N', 'Prefiero no decir'),
]

EDAD_CHOICES = [
    ('14', '14 años'),
    ('15', '15 años'),
    ('16', '16 años'),
    ('17', '17 años'),
    ('18', '18 años'),
]


class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser.
    Incluye campos adicionales para el perfil del estudiante.
    """
    grupo = models.CharField(
        max_length=1,
        choices=GRUPO_CHOICES,
        help_text="Grupo del estudiante (A, B, C, D)"
    )
    
    especialidad = models.CharField(
        max_length=20,
        choices=ESPECIALIDAD_CHOICES,
        help_text="Especialidad del estudiante"
    )
    
    genero = models.CharField(
        max_length=1,
        choices=GENERO_CHOICES,
        help_text="Género del estudiante"
    )
    
    edad = models.CharField(
        max_length=2,
        choices=EDAD_CHOICES,
        help_text="Edad del estudiante"
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.username