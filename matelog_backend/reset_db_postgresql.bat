cat > /home/claude/matelog_backend/reset_db_postgresql.bat << 'EOF'
@echo off
echo ========================================
echo MATELOG - Reset y Migracion PostgreSQL
echo ========================================
echo.

echo [1/6] Activando entorno virtual...
call venv\Scripts\activate

echo.
echo [2/6] Eliminando archivos de migracion antiguos...
del /Q users\migrations\0*.py 2>nul
del /Q lessons\migrations\0*.py 2>nul
del /Q tracking\migrations\0*.py 2>nul

echo.
echo [3/6] Eliminando base de datos SQLite antigua...
del /Q db.sqlite3 2>nul

echo.
echo [4/6] Creando nuevas migraciones...
python manage.py makemigrations users
python manage.py makemigrations lessons
python manage.py makemigrations tracking
python manage.py makemigrations

echo.
echo [5/6] Aplicando migraciones a PostgreSQL...
python manage.py migrate

echo.
echo [6/6] Base de datos PostgreSQL lista!
echo.
echo ========================================
echo SIGUIENTES PASOS:
echo 1. Ejecutar: create_admin.bat
echo 2. Ejecutar: populate.bat
echo 3. Ejecutar: run_server.bat
echo ========================================
echo.
pause
EOF
cat /home/claude/matelog_backend/reset_db_postgresql.bat