# 🎓 MateLog - Plataforma Educativa de Matemáticas

Plataforma web para aprendizaje de matemáticas con sistema de progreso y tracking.

## 🛠️ Stack

- **Backend:** Django 5.0.1 + DRF + PostgreSQL
- **Frontend:** React 18 + Vite
- **Deployment:** Render + Vercel

## 🚀 Instalación Local

### Backend
```bash
cd matelog_backend
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```bash
cd matelog-frontend
npm install
npm run dev
```

## 🌐 URLs

- **Frontend:** https://matelog-USUARIO.vercel.app
- **Backend:** https://matelog-backend.onrender.com
- **Admin:** https://matelog-backend.onrender.com/admin

## 📝 Licencia

MIT