from django.urls import path
from .views import (
    IniciarActividadView,
    FinalizarActividadView,
    IniciarSesionView,
    FinalizarSesionView,
    VolverContenidoView
)

app_name = 'tracking'

urlpatterns = [
    # Tracking de actividad en pantallas
    path('iniciar/', IniciarActividadView.as_view(), name='actividad-iniciar'),
    path('finalizar/', FinalizarActividadView.as_view(), name='actividad-finalizar'),
    path('volver-contenido/', VolverContenidoView.as_view(), name='volver-contenido'),
    
    # Sesiones de estudio
    path('sesion/iniciar/', IniciarSesionView.as_view(), name='sesion-iniciar'),
    path('sesion/finalizar/', FinalizarSesionView.as_view(), name='sesion-finalizar'),
]