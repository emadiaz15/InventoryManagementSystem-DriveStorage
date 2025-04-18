from pydantic_settings import BaseSettings
from typing import Optional
import os
import json

class Settings(BaseSettings):
    # Ruta al JSON de credenciales en disco
    GOOGLE_SERVICE_ACCOUNT_JSON: str 

    # Alternativa: volcar aquí el JSON completo si no existe el fichero
    GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT: Optional[str] = None

    PROFILE_IMAGE_FOLDER_ID: str
    PRODUCTS_IMAGE_FOLDER_ID: str
    SUBPRODUCTS_IMAGE_FOLDER_ID: str
    JWT_SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()

# ------------------------------------------------------------
# Si no existe el fichero en disco, pero sí hemos recibido el
# JSON en la variable de entorno, lo reconstruimos aquí.
# ------------------------------------------------------------
cred_path = settings.GOOGLE_SERVICE_ACCOUNT_JSON

if not os.path.isfile(cred_path):
    if settings.GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT:
        # Aseguramos que exista el directorio
        os.makedirs(os.path.dirname(cred_path), exist_ok=True)
        # Parseamos y volcamos JSON válido
        content = json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT)
        with open(cred_path, "w") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    else:
        raise RuntimeError(
            "No se encontró el fichero de credenciales "
            "ni la variable GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT."
        )
