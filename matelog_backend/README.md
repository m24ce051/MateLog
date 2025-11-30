# MateLog Backend

Backend de la plataforma educativa MateLog construida con Django y Django REST Framework.

## Características

- **Panel de Administración Django**: CRUD completo para lecciones, temas y ejercicios
- **API RESTful**: Endpoints para frontend React
- **Sistema de Progreso**: Tracking detallado del avance de estudiantes
- **Soft Delete**: Lecciones y temas se ocultan en lugar de eliminarse
- **Tracking de Actividad**: Registro de tiempo en cada pantalla
- **Validación Inteligente**: Ignora mayúsculas, espacios y tildes en respuestas abiertas

## Requisitos

- Python 3.8+
- pip

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt --break-system-packages
```

2. Aplicar migraciones (ya aplicadas):
```bash
python manage.py migrate
```

3. Crear superusuario para el admin:
```bash
python manage.py createsuperuser
```

4. Ejecutar servidor de desarrollo:
```bash
python manage.py runserver
```

El servidor estará disponible en `http://localhost:8000`

## Acceso al Panel de Administración

1. Navegar a `http://localhost:8000/admin/`
2. Iniciar sesión con las credenciales del superusuario
3. Gestionar lecciones, temas, ejercicios y usuarios

## Estructura del Proyecto

```
matelog_backend/
├── matelog_backend/        # Configuración principal
├── users/                  # App de usuarios
│   ├── models.py          # CustomUser con campos adicionales
│   ├── serializers.py     # Serializers para API
│   ├── views.py           # Vistas de autenticación
│   └── admin.py           # Admin personalizado
├── lessons/               # App de contenido educativo
│   ├── models.py          # Leccion, Tema, ContenidoTema, Ejercicio
│   ├── serializers.py     # Serializers para API
│   ├── views.py           # Vistas de lecciones y temas
│   └── admin.py           # Admin con inlines
├── tracking/              # App de seguimiento
│   ├── models.py          # Progreso, Respuestas, Actividad
│   ├── serializers.py     # Serializers para tracking
│   ├── views.py           # Vistas de tracking
│   └── admin.py           # Admin con exportación CSV
└── media/                 # Archivos subidos (imágenes)
```

## Endpoints de la API

### Autenticación
- `POST /api/users/register/` - Registro de usuario
- `POST /api/users/login/` - Inicio de sesión
- `POST /api/users/logout/` - Cerrar sesión
- `GET /api/users/profile/` - Perfil del usuario

### Lecciones y Temas
- `GET /api/lessons/` - Lista de lecciones con progreso
- `GET /api/lessons/<id>/` - Detalle de lección con temas
- `GET /api/lessons/temas/<id>/` - Contenido completo del tema
- `POST /api/lessons/temas/<id>/finalizar/` - Finalizar tema
- `POST /api/lessons/temas/<id>/volver/` - Registrar vuelta al tema

### Ejercicios
- `POST /api/lessons/ejercicios/validar/` - Validar respuesta

### Tracking
- `POST /api/tracking/iniciar/` - Iniciar tracking de pantalla
- `POST /api/tracking/finalizar/` - Finalizar tracking de pantalla
- `POST /api/tracking/sesion/iniciar/` - Iniciar sesión de estudio
- `POST /api/tracking/sesion/finalizar/` - Finalizar sesión

## Modelos Principales

### CustomUser
Usuario con campos adicionales: grupo, especialidad, género, edad

### Leccion
- Soft delete con campo `is_active`
- IDs auto-incrementales secuenciales
- Orden de presentación

### Tema
- Pertenece a una Lección
- Contiene ContenidoTema (teoría/ejemplos)
- Contiene Ejercicios
- Soft delete con `is_active`

### ContenidoTema
- Recuadros de TEORIA, EJEMPLO o EJEMPLO_EXTRA
- Soporte para HTML básico e imágenes
- Orden secuencial

### Ejercicio
- Tipos: ABIERTO o MULTIPLE
- Dificultad: FACIL, INTERMEDIO, DIFICIL
- Validación inteligente de respuestas
- Retroalimentación opcional (correcta/incorrecta)
- Texto de ayuda opcional

### ProgresoTema
- Estados: SIN_INICIAR, INICIADO, COMPLETADO
- Desbloqueo automático al 80% de aciertos
- Tracking de intentos correctos/incorrectos

### ActividadPantalla
- Registro de tiempo en cada pantalla
- Timestamps de entrada y salida
- Asociado a lección/tema/ejercicio

## Exportación de Datos

El panel de administración permite exportar a CSV todos los datos de tracking:
1. Ir a la sección de Tracking en el admin
2. Seleccionar registros
3. Elegir "Exportar seleccionados como CSV" del menú de acciones

## Notas Importantes

- **Soft Delete**: No elimines lecciones/temas, usa el campo `is_active`
- **80% para avanzar**: Necesario para desbloquear siguiente tema
- **Validación**: Respuestas abiertas ignoran mayúsculas, espacios y tildes
- **Orden secuencial**: Los estudiantes deben completar lecciones en orden

## Desarrollo

Para agregar contenido de prueba:
1. Acceder al admin
2. Crear Lecciones (con orden 1, 2, 3...)
3. Para cada lección, crear Temas (con orden 1, 2, 3...)
4. Para cada tema, agregar ContenidoTema (teoría/ejemplos)
5. Para cada tema, agregar Ejercicios (~15 por tema recomendado)

## Configuración de CORS

El backend está configurado para aceptar requests de:
- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)

Para agregar otros orígenes, editar `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://tu-frontend-url",
]
```

## Soporte

Para dudas o problemas, revisar:
1. Logs del servidor Django
2. Panel de administración
3. Consola del navegador (para errores de API)
