from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_SERVICE_ACCOUNT_JSON: str
    PROFILE_IMAGE_FOLDER_ID: str
    PRODUCTS_IMAGE_FOLDER_ID: str
    SUBPRODUCTS_IMAGE_FOLDER_ID: str
    JWT_SECRET_KEY: str  # 🔐 Clave secreta para verificar los tokens JWT emitidos por Django

    class Config:
        env_file = ".env"

settings = Settings()
