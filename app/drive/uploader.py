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

# --- Crea una subcarpeta si no existe ---
def get_or_create_subfolder(name: str, parent_id: str) -> str:
    service = get_drive_service()
    query = f"name='{name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])
    if folders:
        return folders[0]['id']

    folder_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    return folder.get("id")

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

# --- Eliminar archivo por ID ---
def delete_file(file_id: str) -> None:
    service = get_drive_service()
    service.files().delete(fileId=file_id).execute()

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

def upload_product_image(file: UploadFile, product_id: str) -> str:
    product_folder_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID)
    return upload_file_to_folder(file.file.read(), file.filename, file.content_type, product_folder_id)

def upload_subproduct_image(file: UploadFile, subproduct_id: str, product_id: str) -> str:
    product_folder_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID)
    subproduct_folder_id = get_or_create_subfolder(subproduct_id, product_folder_id)
    return upload_file_to_folder(file.file.read(), file.filename, file.content_type, subproduct_folder_id)

def list_product_images(product_id: str) -> list[dict]:
    service = get_drive_service()
    product_folder_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID)
    query = f"'{product_folder_id}' in parents and trashed = false"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType, createdTime, modifiedTime)',
    ).execute()
    return results.get('files', [])

def list_subproduct_images(subproduct_id: str, product_id: str) -> list[dict]:
    service = get_drive_service()
    product_folder_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID)
    subproduct_folder_id = get_or_create_subfolder(subproduct_id, product_folder_id)
    query = f"'{subproduct_folder_id}' in parents and trashed = false"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType, createdTime, modifiedTime)',
    ).execute()
    return results.get('files', [])

def replace_product_image(file: UploadFile, product_id: str, file_id: str) -> str:
    return replace_file(file_id, file.file.read(), file.filename, file.content_type)

def replace_subproduct_image(file: UploadFile, subproduct_id: str, file_id: str) -> str:
    return replace_file(file_id, file.file.read(), file.filename, file.content_type)

def delete_product_image(file_id: str) -> None:
    delete_file(file_id)

def delete_subproduct_image(file_id: str) -> None:
    delete_file(file_id)

def download_product_image(file_id: str) -> tuple[bytes, str]:
    metadata = get_file_metadata(file_id)
    content = download_file(file_id)
    return content, metadata.get("name")

def download_subproduct_image(file_id: str) -> tuple[bytes, str]:
    metadata = get_file_metadata(file_id)
    content = download_file(file_id)
    return content, metadata.get("name")
