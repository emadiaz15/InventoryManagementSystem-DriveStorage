import os
from fastapi import HTTPException
from app.drive.config import settings

def validate_file_extension(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Extensión de archivo no permitida: {ext}")
    return ext
