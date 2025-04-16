from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Ruta donde se escribirá el archivo (si hace falta)
    GOOGLE_SERVICE_ACCOUNT_JSON: str = "credentials/service_account.json"

    # En entorno de producción se usará esta variable para reconstruir el archivo
    GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT: Optional[str] = None

    PROFILE_IMAGE_FOLDER_ID: str
    PRODUCTS_IMAGE_FOLDER_ID: str
    SUBPRODUCTS_IMAGE_FOLDER_ID: str
    JWT_SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()

# ⚙️ Reconstruir archivo de credenciales si no existe y estamos en producción
if not os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_JSON):
    if settings.GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT:
        os.makedirs(os.path.dirname(settings.GOOGLE_SERVICE_ACCOUNT_JSON), exist_ok=True)
        with open(settings.GOOGLE_SERVICE_ACCOUNT_JSON, "w") as f:
            f.write(settings.GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT)
    else:
        raise ValueError("No se encontró el archivo de credenciales ni la variable GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT.")
