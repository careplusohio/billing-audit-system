# CarePlus Audit System

A secure healthcare billing audit platform built with Django, React, and PostgreSQL. Features include role-based dashboards, audit flagging, data export, and CSV uploads with real-time validation.

---

## 🚀 Deployment Options

### Option 1: Dockerized Production (Recommended)

1. **Build and start containers**
```bash
docker-compose up --build
```

2. **Run initial Django setup**
```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --noinput
```

3. **Access your app**
- Frontend: http://localhost
- Admin: http://localhost/api/admin/

---

### Option 2: Local React Development

1. Start backend (Docker or local Django runserver)
2. In new terminal:
```bash
cd frontend
npm install
npm start
```
3. Visit: http://localhost:3000

---

## 🔐 Environment Variables

Create a `.env` file using `.env.example` for safe defaults.

---

## ✉️ API Highlights

- JWT-based authentication
- CSV upload with validation and audit flagging
- PDF, CSV, ZIP export endpoints
- Patient, Provider, and Visit modules

---

## 📦 Project Structure

```
backend/
  patients/
  providers/
  visits/
  audits/
  authentication/
frontend/
  src/components/
  Dockerfile
docker-compose.yml
```

---

## ⚙ Tech Stack

- Django + DRF + PostgreSQL
- React + Tailwind + Axios
- Docker + Gunicorn + Nginx
- WeasyPrint for PDF rendering

---

## 📄 License

© 2025 CarePlus Ohio – Internal Use Only