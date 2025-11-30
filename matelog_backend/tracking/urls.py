from django.urls import path
from .views import (
    IniciarSesionView,
    FinalizarSesionView,
    IniciarActividadView,
    FinalizarActividadView,
    RegistrarVolverContenidoView,
)

urlpatterns = [
    # Sesiones de estudio
    path('sesion/iniciar/', IniciarSesionView.as_view(), name='iniciar-sesion'),
    path('sesion/finalizar/', FinalizarSesionView.as_view(), name='finalizar-sesion'),
    
    # Actividades de pantalla
    path('iniciar/', IniciarActividadView.as_view(), name='iniciar-actividad'),
    path('finalizar/', FinalizarActividadView.as_view(), name='finalizar-actividad'),
    
    # Modificación 4: Tracking de botón "Volver"
    path('volver-contenido/', RegistrarVolverContenidoView.as_view(), name='volver-contenido'),
]