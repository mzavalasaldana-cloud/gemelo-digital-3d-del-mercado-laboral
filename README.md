# 🌐 Gemelo Digital 3D del Mercado Laboral y Transición a la Formalidad

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/mzavalasaldana-cloud/gemelo-digital-3d-del-mercado-laboral)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/mzavalasaldana-cloud/gemelo-digital-3d-del-mercado-laboral)

Simulador macro y microeconómico multiagente basado en Inteligencia Artificial y Three.js para modelar el impacto de políticas de formalización laboral según estándares de la OIT y ODS 8.

---

## 🏗️ Arquitectura de Despliegue

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│        Vercel (Frontend)        │       │         Render (Backend)        │
│   React 19 + Vite + Three.js    │ ────> │ FastAPI + Python 3.11 + Uvicorn │
│  https://<tu-app>.vercel.app    │ <──── │ https://<tu-api>.onrender.com   │
└─────────────────────────────────┘       └─────────────────────────────────┘
                │                                         │
          REST / WebSockets                         REST / WebSockets
                │                                         │
                └─────────────────┬───────────────────────┘
                                  ▼
                 ┌─────────────────────────────────┐
                 │       Streamlit Cloud           │
                 │      (Dashboard Ejecutivo)      │
                 │     streamlit_app/app.py        │
                 └─────────────────────────────────┘
```

---

## 🚀 Despliegue Rápido (1-Click)

### 1. Backend en Render
1. Haz clic en el botón **Deploy to Render**:
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/mzavalasaldana-cloud/gemelo-digital-3d-del-mercado-laboral)
2. Render leerá automáticamente la configuración de [`render.yaml`](./render.yaml).
3. Una vez termine el despliegue, copia la URL asignada (ejemplo: `https://gemelo-laboral-backend.onrender.com`).

### 2. Frontend en Vercel
1. Haz clic en el botón **Deploy with Vercel**:
   [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/mzavalasaldana-cloud/gemelo-digital-3d-del-mercado-laboral)
2. Agrega la variable de entorno:
   - **Nombre:** `VITE_API_URL`
   - **Valor:** `https://gemelo-laboral-backend.onrender.com` (la URL de tu backend en Render sin barra al final).
3. Haz clic en **Deploy**.

### 3. Dashboard Streamlit en Streamlit Cloud
1. Entra a [share.streamlit.io](https://share.streamlit.io/).
2. Conecta este repositorio (`gemelo-digital-3d-del-mercado-laboral`) y rama `main`.
3. Establece el **Main file path** en `app.py`.
4. ¡Listo! Ya cuenta con **Modo Claro** nativo por defecto y selector de tema.

---

## 💻 Ejecución Local

### Frontend (React + Vite)
```bash
npm install
npm run dev
# Disponible en http://localhost:3000
```

### Backend (FastAPI)
```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
# Disponible en http://localhost:8000/docs
```

### Streamlit App
```bash
streamlit run app.py
# Disponible en http://localhost:8501
```
