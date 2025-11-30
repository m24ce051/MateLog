#!/bin/bash
# matelog_backend/build.sh

echo "🚀 Iniciando despliegue MateLog..."

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# CREAR SUPERUSER SI NO EXISTE
echo "🔧 Verificando superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@matelog.com',
        password='matelog123'
    )
    print('✅ Superusuario admin creado')
else:
    print('⚠️ Superusuario ya existe')
"

# Colectar archivos estáticos
python manage.py collectstatic --noinput

echo "✅ Despliegue completado"
