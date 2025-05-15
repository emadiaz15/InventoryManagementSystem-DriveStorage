import os
import json
from googleapiclient.discovery import build                       # 📦 Constructor del servicio de Google Drive
from google.oauth2 import service_account                         # 🔐 Autenticación vía service account
from app.drive.config import settings                             # ⚙️ Configuración central (env vars, rutas, etc.)

def get_drive_service():
    """
    🔌 Inicializa y retorna un cliente autenticado de Google Drive API v3.

    La autenticación se hace mediante un JSON de Service Account, que puede ser:
    - Un archivo físico en el sistema.
    - Un string con el contenido del JSON embebido (ideal para Docker/secrets/env vars).

    Returns:
        googleapiclient.discovery.Resource: Cliente de la API de Drive.
    """
    scopes = ["https://www.googleapis.com/auth/drive"]  # Permiso completo para manipular Drive
    json_path = settings.GOOGLE_SERVICE_ACCOUNT_JSON     # Ruta al archivo físico (si existe)

    if os.path.isfile(json_path):
        # ✅ Si el archivo físico existe, se usa directamente
        creds = service_account.Credentials.from_service_account_file(
            json_path,
            scopes=scopes
        )
    else:
        # 🧠 Si no hay archivo, se intenta con el contenido de JSON embebido
        info = json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT or "{}")

        # 🔧 Corrige el formato del private_key (los \n vienen escapados en .env)
        if isinstance(info.get("private_key"), str):
            info["private_key"] = info["private_key"].replace("\\n", "\n")

        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)

    # 📦 Devuelve el cliente autenticado listo para usar
    return build("drive", "v3", credentials=creds)
