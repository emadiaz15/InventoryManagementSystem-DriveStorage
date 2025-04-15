# Inventory Drive Storage API

Este proyecto es una **API externa** construida con **FastAPI** para manejar el almacenamiento de imágenes en **Google Drive**, utilizada como backend de archivos para un sistema principal desarrollado en **Django**.

## 🚀 Características

- Subida de imágenes por tipo: perfil, productos y subproductos.
- Reemplazo, listado y descarga de archivos.
- Carpeta principal estructurada en subcarpetas por tipo.
- Acceso autenticado mediante **JWT** (entre servicios).
- Configuración vía `.env`.

## 📂 Estructura del Proyecto

```
Inventory-Drive-Storage/
├── app/
│   └── drive/
│       ├── auth.py
│       ├── config.py
│       ├── uploader.py
│       └── routes/
│           ├── profile_routes.py
│           ├── product_routes.py
│           └── subproduct_routes.py
├── credentials/
│   └── service_account.json
├── .env
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## 🔐 Variables de Entorno (.env)

```env
GOOGLE_SERVICE_ACCOUNT_JSON=credentials/service_account.json
PROFILE_IMAGE_FOLDER_ID=<id_de_la_carpeta_de_perfiles>
PRODUCTS_IMAGE_FOLDER_ID=<id_de_la_carpeta_de_productos>
SUBPRODUCTS_IMAGE_FOLDER_ID=<id_de_la_carpeta_de_subproductos>
JWT_SECRET_KEY=tu_clave
```

> ⚠️ No uses las URLs de carpetas públicas. Solo IDs directos desde Google Drive.

## 🛠 Instalación

```bash
# Crear entorno virtual
python -m venv env
source env/bin/activate  # Linux/macOS
env\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## 🚦 Ejecución local

```bash
uvicorn main:app --reload
```

Accede a la documentación automática en:

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔗 Integración con Django

Desde Django:

1. Generar un JWT firmado con la misma clave (`JWT_SECRET_KEY`).
2. Enviar las peticiones a FastAPI incluyendo en headers:

```http
Authorization: Bearer <JWT_TOKEN>
```

3. Usar los endpoints:

- `/profile/` para imagen de perfil.
- `/product/{product_id}/upload` y asociados.
- `/subproduct/{subproduct_id}/upload` y asociados.

## 📦 Construido con

- [FastAPI](https://fastapi.tiangolo.com/)
- [Google Drive API](https://developers.google.com/drive)
- [python-jose](https://pypi.org/project/python-jose/)
- [Uvicorn](https://www.uvicorn.org/)

---
