from pydantic_settings import BaseSettings
from typing import Optional, List
from pydantic import field_validator
import json
import os

class Settings(BaseSettings):
    GOOGLE_SERVICE_ACCOUNT_JSON: str
    GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT: Optional[str] = None

    PROFILE_IMAGE_FOLDER_ID: str
    PRODUCTS_IMAGE_FOLDER_ID: str
    SUBPRODUCTS_IMAGE_FOLDER_ID: Optional[str] = None
    JWT_SECRET_KEY: str

    ALLOWED_ORIGINS: List[str]
    ALLOWED_EXTENSIONS: List[str] = [
        ".jpg", ".jpeg", ".png", ".webp",
        ".mp4", ".mov", ".avi", ".webm", ".mkv", ".pdf"
    ]
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                raise ValueError("Formato inválido para ALLOWED_ORIGINS, se esperaba JSON válido.")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# --- Reconstrucción segura del archivo de credenciales ---
cred_path = settings.GOOGLE_SERVICE_ACCOUNT_JSON

if not os.path.isfile(cred_path):
    if settings.GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT:
        os.makedirs(os.path.dirname(cred_path), exist_ok=True)
        try:
            content = json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT)
        except json.JSONDecodeError:
            raise RuntimeError("Contenido de GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT inválido.")
        with open(cred_path, "w") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    else:
        raise RuntimeError(
            "❌ No se encontró el fichero de credenciales "
            "ni la variable GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT."
        )
