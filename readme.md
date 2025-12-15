# 🚀 Guía para ejecutar el proyecto localmente

Esta guía explica cómo **clonar y levantar el proyecto completo (backend + frontend)** en un entorno local.

---

## 1️⃣ Requisitos previos

Asegúrate de tener instalado:

- **Git**
- **Python 3.10 o superior**
- **Node.js 18 o superior**
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

---

### 🧪 Crear entorno virtual

```bash
python -m venv venv
```

---

### ▶️ Activar el entorno virtual

**Windows**
```bash
venv\Scripts\activate
```

**Linux / macOS**
```bash
source venv/bin/activate
```

Cuando esté activo verás:

```text
(venv)
```

---

### 📦 Instalar dependencias

```bash
pip install -r requirements.txt
```

---

### 🔐 Crear archivo `.env`

Crear el archivo:

```text
backend/.env
```

Contenido:

```env
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=mi_base
```

> ⚠️ Si usas MongoDB Atlas, reemplaza `MONGODB_URI` con tu URI.

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

## ⭐ Notas finales

- No subir `venv/` ni `.env` al repositorio
- Cada desarrollador crea su propio entorno local
- `requirements.txt` y `package.json` garantizan consistencia

---

✅ Con estos pasos el proyecto debería correr sin problemas en cualquier máquina.

