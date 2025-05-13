import io
import os
import mimetypes
from fastapi import UploadFile, HTTPException
from googleapiclient.http import MediaIoBaseUpload

from app.drive.config import settings
from .client import get_drive_service                         # 🔌 Cliente autenticado de Google Drive
from app.drive.utils.validations import validate_file_extension  # ✅ Usando la función movida a utils


def prepare_update(file: UploadFile, new_filename: str):
    """
    🧪 Valida y prepara el archivo para ser reemplazado en Google Drive.

    Args:
        file: UploadFile recibido en el PUT/PATCH.
        new_filename: Nombre con el que será renombrado el archivo.

    Returns:
        Tuple con datos binarios, nombre y tipo MIME.
    """
    ext = validate_file_extension(file.filename)  # Validación de extensión desde utils
    data = file.file.read()                       # Leemos el contenido binario
    mimetype = file.content_type or mimetypes.guess_type(file.filename)[0]  # Detectamos MIME si no viene
    return data, new_filename, mimetype


def replace_file(file_id: str, file: UploadFile, new_filename: str, service=None) -> str:
    """
    🔁 Reemplaza el contenido y nombre de un archivo existente en Google Drive.

    Args:
        file_id: ID del archivo en Drive que será reemplazado.
        file: Nuevo archivo subido desde el cliente.
        new_filename: Nuevo nombre que tendrá el archivo.
        service: Cliente de Drive (opcional, para testeo o mockeo).

    Returns:
        ID del archivo actualizado (usualmente igual al original).
    """
    service = service or get_drive_service()

    # Preparamos el nuevo archivo
    data, name, mimetype = prepare_update(file, new_filename)

    # Construimos el cuerpo de actualización
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype or "application/octet-stream", resumable=True)

    # Ejecutamos el update vía API
    updated = service.files().update(
        fileId=file_id,
        media_body=media,
        body={"name": name}
    ).execute()

    return updated["id"]

