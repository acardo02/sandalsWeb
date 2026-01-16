# 🛍️ Sandals Web - E-commerce Platform

Plataforma completa de e-commerce para productos artesanales construida con **FastAPI** y **SvelteKit**.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.124-green.svg)](https://fastapi.tiangolo.com/)
[![Svelte](https://img.shields.io/badge/Svelte-5-orange.svg)](https://svelte.dev/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://www.mongodb.com/)

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Ejecución](#-ejecución)
- [API Endpoints](#-api-endpoints)
- [Seguridad](#-seguridad)
- [Testing](#-testing)
- [Despliegue](#-despliegue)

---

## ✨ Características

### Backend (FastAPI)
- ✅ Autenticación JWT con bcrypt
- ✅ Rate limiting (5 intentos/min en login)
- ✅ Validación robusta de contraseñas
- ✅ Actualizaciones atómicas para prevenir race conditions
- ✅ Logging de acciones críticas
- ✅ CORS configurado
- ✅ Documentación automática (Swagger/ReDoc)

### Frontend (SvelteKit)
- ✅ SSR (Server-Side Rendering)
- ✅ State management con Svelte stores
- ✅ Lazy loading de imágenes
- ✅ Debounced search
- ✅ Validación de stock en tiempo real
- ✅ Responsive design

### Funcionalidades
- 🛒 Carrito de compras
- 📦 Gestión de productos (CRUD)
- 👤 Autenticación de usuarios
- 🔐 Panel de administración
- 📊 Gestión de órdenes
- 🔍 Búsqueda y filtros
- 🖼️ Upload de imágenes (Cloudinary)

---

## 🏗️ Arquitectura

```
sandalsWeb/
├── backend/          # FastAPI + MongoDB
│   ├── app/
│   │   ├── core/     # Config, security, dependencies
│   │   ├── models/   # Beanie models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── routes/   # API endpoints
│   │   ├── services/ # Business logic
│   │   └── db/       # Database connection
│   ├── scripts/      # Utility scripts
│   └── tests/        # Pytest tests
│
└── frontend/         # SvelteKit
    ├── src/
    │   ├── routes/   # SvelteKit routes
    │   ├── lib/
    │   │   ├── components/
    │   │   ├── stores/
    │   │   └── utils/
    │   └── app.html
    └── static/
```

---

## 1️⃣ Requisitos Previos

Asegúrate de tener instalado:

- **Git**
- **Python 3.10 o superior**
- **Node.js 20 o superior**
- **MongoDB** (local o MongoDB Atlas)

Verificar versiones:

```bash
git --version
python --version
node --version
npm --version
```

---

## 2️⃣ Clonar el repositorio

```bash
git clone https://github.com/USUARIO/NOMBRE-DEL-REPO.git
cd NOMBRE-DEL-REPO
```

Estructura esperada:

```text
mi-proyecto/
├── backend/
└── frontend/
```

---

## 3️⃣ Backend (FastAPI + MongoDB)

### 📁 Entrar al backend

```bash
cd backend
```

### 🧪 Crear entorno virtual

```bash
python -m venv venv
```

### ▶️ Activar el entorno virtual

**Windows**
```bash
venv\Scripts\activate
```

**Linux / macOS**
```bash
source venv/bin/activate
```

### 📦 Instalar dependencias

```bash
pip install -r requirements.txt
```

### 🔐 Configurar variables de entorno

1. Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

2. Edita `.env` y configura las variables:

```env
# Application
PROJECT_NAME="Sandals API"
ENVIRONMENT=development

# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=sandals_db

# Security - GENERAR NUEVA CLAVE con: python -c "import secrets; print(secrets.token_urlsafe(64))"
SECRET_KEY=<tu_clave_secreta_aqui>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Admin creation (solo true para crear admin inicial)
ALLOW_ADMIN_CREATION=false

# Cloudinary (Image hosting)
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret

# CORS
CORS_ORIGINS=http://localhost:5173
```

### 👤 Crear usuario administrador

```bash
python -m scripts.create_admin
```

Sigue las instrucciones en pantalla para crear tu admin.

---

### ▶️ Ejecutar el backend

```bash
uvicorn app.main:app --reload
```

Backend disponible en:

```
http://localhost:8000
```

Documentación automática:

```
http://localhost:8000/docs
```

---

## 4️⃣ Frontend (SvelteKit)

> Abre **otra terminal** (no cierres la del backend).

---

### 📁 Entrar al frontend

```bash
cd frontend
```

---

### 📦 Instalar dependencias

```bash
npm install
```

---

### 🔐 Crear archivo `.env`

```text
frontend/.env
```

Contenido:

```env
VITE_API_URL=http://localhost:8000
```

---

### ▶️ Ejecutar el frontend

```bash
npm run dev
```

Frontend disponible en:

```
http://localhost:5173
```

---

## 5️⃣ Verificación rápida

1. Backend corriendo en `http://localhost:8000/docs`
2. Frontend corriendo en `http://localhost:5173`
3. El frontend debe consumir la API sin errores

---

## 6️⃣ Problemas comunes

### ❌ Error de CORS

Verificar que el backend permita el origen:

```python
allow_origins=["http://localhost:5173"]
```

---

### ❌ Error de conexión a MongoDB

- Asegúrate de que MongoDB esté activo
- Verifica las variables del archivo `.env`

---

### ❌ Comando no reconocido

- Verifica las versiones de Python y Node
- Asegúrate de haber activado el entorno virtual

---

## 7️⃣ Detener el proyecto

En cada terminal:

```text
CTRL + C
```

---

## 📚 API Endpoints

### Autenticación
```
POST   /auth/login          - Login de usuario (rate limit: 5/min)
POST   /auth/register       - Registro de usuario
POST   /auth/register-admin - Crear admin (controlado por env)
```

### Usuarios
```
GET    /users/              - Listar usuarios (admin)
GET    /users/me            - Obtener perfil actual
```

### Productos
```
GET    /products/           - Listar productos (con filtros)
GET    /products/{id}       - Detalle de producto
POST   /products/           - Crear producto (admin)
PATCH  /products/{id}       - Actualizar producto (admin)
DELETE /products/{id}       - Eliminar producto (admin)
```

### Órdenes
```
POST   /orders/             - Crear orden
GET    /orders/me           - Mis órdenes
GET    /orders/             - Todas las órdenes (admin)
PATCH  /orders/{id}/status  - Actualizar estado (admin)
```

### Upload
```
POST   /upload/             - Subir imagen
```

**Documentación interactiva:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🔒 Seguridad

### Mejores Prácticas Implementadas

✅ **Autenticación robusta:**
- JWT tokens con expiración (60 min)
- Contraseñas hasheadas con bcrypt
- Validación de fortaleza de contraseña

✅ **Rate limiting:**
- Login: 5 intentos por minuto por IP
- Previene ataques de fuerza bruta

✅ **Validaciones:**
- Pydantic para validación de datos
- Validación de stock antes de órdenes
- Actualizaciones atómicas en MongoDB

✅ **CORS configurado:**
- Solo orígenes permitidos
- Métodos y headers específicos

✅ **Logging:**
- Acciones críticas registradas
- Login attempts, errors, etc.

---

## 🧪 Testing

### Backend
```bash
cd backend
pytest
pytest --cov=app tests/
```

### Frontend
```bash
cd frontend
npm run test
npm run test:ui
```

---

## 🚀 Despliegue

### Backend (Railway/Render/Heroku)

1. Configurar variables de entorno en la plataforma
2. Usar MongoDB Atlas para producción
3. Configurar CORS_ORIGINS con dominio de producción
4. Establecer ENVIRONMENT=production

### Frontend (Vercel/Netlify)

1. Configurar VITE_API_URL con URL de producción
2. Build automático con adaptador apropiado
3. Variables de entorno en la plataforma

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Add: nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

---

## ⭐ Notas finales

- **No subir** `venv/`, `.env`, `node_modules/` al repositorio
- Cada desarrollador crea su propio entorno local
- `requirements.txt` y `package.json` garantizan consistencia
- Revisa los archivos `.env.example` para ver todas las variables necesarias

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

✅ Con estos pasos el proyecto debería correr sin problemas en cualquier máquina.

