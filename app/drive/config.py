from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    GOOGLE_SERVICE_ACCOUNT_JSON: str = "credentials/service_account.json"
    GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT: str  # ← desde env
    PROFILE_IMAGE_FOLDER_ID: str
    PRODUCTS_IMAGE_FOLDER_ID: str
    SUBPRODUCTS_IMAGE_FOLDER_ID: str
    JWT_SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()

# 📝 Escribir archivo de credenciales si no existe (Railway o producción)
if not os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_JSON):
    os.makedirs(os.path.dirname(settings.GOOGLE_SERVICE_ACCOUNT_JSON), exist_ok=True)
    with open(settings.GOOGLE_SERVICE_ACCOUNT_JSON, "w") as f:
        f.write(settings.GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT)
