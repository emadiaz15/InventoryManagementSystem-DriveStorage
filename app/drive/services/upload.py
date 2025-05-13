import io
import os
import mimetypes
from fastapi import UploadFile
from googleapiclient.http import MediaIoBaseUpload

from app.drive.config import settings
from .client import get_drive_service                     # 🔌 Inicializa cliente Google Drive
from .folders import get_or_create_subfolder              # 📁 Maneja carpetas anidadas en Drive
from app.drive.utils.validations import validate_file_extension  # ✅ Validación de extensiones (ahora en utils)

# 📤 Subir archivo genérico a una carpeta en Google Drive
def upload_file_to_folder(data: bytes, filename: str, mimetype: str, folder_id: str, service=None) -> str:
    """
    Sube un archivo (bytes) a una carpeta específica en Google Drive.

    Args:
        data: Contenido binario del archivo.
        filename: Nombre que tendrá el archivo en Drive.
        mimetype: Tipo MIME del archivo.
        folder_id: ID de la carpeta en Drive.
        service: Cliente de Google Drive, opcional.

    Returns:
        ID del archivo creado en Drive.
    """
    service = service or get_drive_service()
    metadata = {"name": filename, "parents": [folder_id]}  # 📄 Metadata básica para el archivo
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype or "application/octet-stream", resumable=True)
    file = service.files().create(body=metadata, media_body=media, fields="id").execute()
    return file["id"]

# 🧪 Prepara archivo subido para Drive (validación, lectura de bytes, MIME)
def prepare_upload(file: UploadFile):
    """
    Valida y procesa un archivo de FastAPI antes de subirlo a Google Drive.

    Args:
        file: Objeto UploadFile recibido desde un formulario HTTP.

    Returns:
        Tuple con contenido binario, extensión y MIME type.
    """
    ext = validate_file_extension(file.filename)  # Verifica que la extensión esté permitida
    data = file.file.read()
    mimetype = file.content_type or mimetypes.guess_type(file.filename)[0]
    return data, ext, mimetype

# 📦 Subida específica para subproductos: crea carpetas anidadas y sube archivo
def upload_subproduct_image(file: UploadFile, subproduct_id: str, product_id: str, service=None) -> str:
    """
    Sube una imagen asociada a un subproducto dentro de la jerarquía /PRODUCTO_ID/SUBPRODUCTO_ID/

    Args:
        file: Archivo a subir (desde FastAPI).
        subproduct_id: ID único del subproducto.
        product_id: ID del producto padre.
        service: Cliente de Google Drive (opcional, para tests o inyección).

    Returns:
        ID del archivo creado en Drive.
    """
    service = service or get_drive_service()

    # Procesamiento de archivo (validación y extracción de datos)
    data, ext, mimetype = prepare_upload(file)
    filename = file.filename  # Se mantiene nombre original

    # Crear carpetas /producto/subproducto/ si no existen
    parent_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID, service)
    subfolder_id = get_or_create_subfolder(subproduct_id, parent_id, service)

    # Subir archivo al folder del subproducto
    return upload_file_to_folder(data, filename, mimetype, subfolder_id, service)
