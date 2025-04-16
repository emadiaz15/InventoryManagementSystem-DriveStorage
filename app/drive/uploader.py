import io
import json
from typing import Optional
from fastapi import UploadFile
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from google.oauth2 import service_account
from .config import settings


# --- Inicializa el servicio de Google Drive ---
def get_drive_service():
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT),
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=credentials)


# --- Subida genérica a una carpeta ---
def upload_file_to_folder(file, filename: str, mimetype: str, folder_id: str) -> str:
    service = get_drive_service()

    file_metadata = {
        "name": filename,
        "parents": [folder_id]
    }

    media = MediaIoBaseUpload(io.BytesIO(file), mimetype=mimetype, resumable=True)
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    return uploaded_file.get("id")


# --- Reemplazo de archivo por ID ---
def replace_file(file_id: str, new_file_data: bytes, new_filename: str, mimetype: str):
    service = get_drive_service()

    media = MediaIoBaseUpload(io.BytesIO(new_file_data), mimetype=mimetype, resumable=True)

    updated_file = service.files().update(
        fileId=file_id,
        media_body=media,
        body={"name": new_filename}
    ).execute()

    return updated_file.get("id")


# --- Obtener metadatos del archivo ---
def get_file_metadata(file_id: str) -> dict:
    service = get_drive_service()
    metadata = service.files().get(fileId=file_id).execute()
    return metadata


# --- Descargar archivo desde Drive ---
def download_file(file_id: str) -> bytes:
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    return file_data.getvalue()


# ===============================
# Funciones para integración con FastAPI
# ===============================

def list_subproduct_images(subproduct_id: str) -> list[dict]:
    """
    Lista las imágenes de subproducto según su folder_id.
    Nota: Actualmente retorna todos los archivos en la carpeta de subproductos.
    """
    service = get_drive_service()
    query = f"'{settings.SUBPRODUCTS_IMAGE_FOLDER_ID}' in parents and trashed = false"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType, createdTime, modifiedTime)',
    ).execute()

    return results.get('files', [])


def list_product_images(product_id: str) -> list[dict]:
    """
    Lista las imágenes de producto según su folder_id.
    Nota: Actualmente retorna los archivos de la carpeta general de productos.
    Si querés que cada producto tenga su propia carpeta, esto debería adaptarse.
    """
    service = get_drive_service()
    query = f"'{settings.PRODUCTS_IMAGE_FOLDER_ID}' in parents and trashed = false"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType, createdTime, modifiedTime)',
    ).execute()

    return results.get('files', [])

def upload_file(file: UploadFile, folder_type: str = "profile") -> str:
    """
    Sube un archivo a la carpeta correspondiente según el tipo (profile, product, subproduct).
    """
    folder_map = {
        "profile": settings.PROFILE_IMAGE_FOLDER_ID,
        "product": settings.PRODUCTS_IMAGE_FOLDER_ID,
        "subproduct": settings.SUBPRODUCTS_IMAGE_FOLDER_ID,
    }

    folder_id = folder_map.get(folder_type)
    if not folder_id:
        raise ValueError(f"Invalid folder_type: {folder_type}")

    file_content = file.file.read()
    return upload_file_to_folder(file_content, file.filename, file.content_type, folder_id)


def upload_product_image(file: UploadFile, product_id: str) -> str:
    return upload_file_to_folder(file.file.read(), file.filename, file.content_type, settings.PRODUCTS_IMAGE_FOLDER_ID)


def upload_subproduct_image(file: UploadFile, subproduct_id: str) -> str:
    return upload_file_to_folder(file.file.read(), file.filename, file.content_type, settings.SUBPRODUCTS_IMAGE_FOLDER_ID)


def replace_product_image(file: UploadFile, product_id: str, file_id: str) -> str:
    return replace_file(file_id, file.file.read(), file.filename, file.content_type)


def replace_subproduct_image(file: UploadFile, subproduct_id: str, file_id: str) -> str:
    return replace_file(file_id, file.file.read(), file.filename, file.content_type)


def download_product_image(file_id: str) -> tuple[bytes, str]:
    metadata = get_file_metadata(file_id)
    content = download_file(file_id)
    return content, metadata.get("name")


def download_subproduct_image(file_id: str) -> tuple[bytes, str]:
    metadata = get_file_metadata(file_id)
    content = download_file(file_id)
    return content, metadata.get("name")
