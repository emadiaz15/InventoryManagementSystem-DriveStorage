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
    query = (
        f"name='{name}' and '{parent_id}' in parents "
        "and mimeType='application/vnd.google-apps.folder' and trashed=false"
    )
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

# --- Operaciones de bajo nivel: carga, reemplazo, eliminación, metadatos, descarga ---

def _upload_file_to_folder(data: bytes, filename: str, mimetype: str, folder_id: str) -> str:
    service = get_drive_service()
    file_metadata = {"name": filename, "parents": [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype=mimetype, resumable=True)
    created = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    return created.get("id")


def _replace_file_raw(file_id: str, data: bytes, new_filename: str, mimetype: str) -> str:
    service = get_drive_service()
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype=mimetype, resumable=True)
    updated = service.files().update(
        fileId=file_id,
        media_body=media,
        body={"name": new_filename}
    ).execute()
    return updated.get("id")


def delete_file(file_id: str) -> None:
    service = get_drive_service()
    service.files().delete(fileId=file_id).execute()


def get_file_metadata(file_id: str) -> dict:
    service = get_drive_service()
    return service.files().get(fileId=file_id).execute()


def download_file(file_id: str) -> bytes:
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buffer.getvalue()

# ===============================
# Wrappers de alto nivel para FastAPI
# ===============================

def upload_file(file: UploadFile, folder_type: str) -> str:
    """
    Sube un UploadFile al tipo de carpeta indicado:
      - "profile"    → settings.PROFILE_IMAGE_FOLDER_ID
      - "product"    → settings.PRODUCTS_IMAGE_FOLDER_ID
      - "subproduct" → settings.SUBPRODUCTS_IMAGE_FOLDER_ID
    """
    content = file.file.read()
    filename = file.filename
    mimetype = file.content_type

    if folder_type == "profile":
        folder_id = settings.PROFILE_IMAGE_FOLDER_ID
    elif folder_type == "product":
        folder_id = settings.PRODUCTS_IMAGE_FOLDER_ID
    elif folder_type == "subproduct":
        folder_id = settings.SUBPRODUCTS_IMAGE_FOLDER_ID
    else:
        raise ValueError(f"Tipo de carpeta inválido: {folder_type}")

    return _upload_file_to_folder(content, filename, mimetype, folder_id)


def replace_file(file_id: str, new_file: UploadFile) -> str:
    """
    Reemplaza un archivo existente dado un UploadFile:
    """
    data = new_file.file.read()
    filename = new_file.filename
    mimetype = new_file.content_type
    return _replace_file_raw(file_id, data, filename, mimetype)


def upload_product_image(file: UploadFile, product_id: str) -> str:
    product_folder_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID)
    return _upload_file_to_folder(file.file.read(), file.filename, file.content_type, product_folder_id)


def upload_subproduct_image(file: UploadFile, subproduct_id: str, product_id: str) -> str:
    parent_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID)
    subfolder_id = get_or_create_subfolder(subproduct_id, parent_id)
    return _upload_file_to_folder(file.file.read(), file.filename, file.content_type, subfolder_id)


def list_product_images(product_id: str) -> list[dict]:
    folder_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID)
    query = f"'{folder_id}' in parents and trashed=false"
    results = get_drive_service().files().list(
        q=query,
        spaces='drive',
        fields='files(id,name,mimeType,createdTime,modifiedTime)'
    ).execute()
    return results.get('files', [])


def list_subproduct_images(subproduct_id: str, product_id: str) -> list[dict]:
    parent_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID)
    folder_id = get_or_create_subfolder(subproduct_id, parent_id)
    query = f"'{folder_id}' in parents and trashed=false"
    results = get_drive_service().files().list(
        q=query,
        spaces='drive',
        fields='files(id,name,mimeType,createdTime,modifiedTime)'
    ).execute()
    return results.get('files', [])


def replace_product_image(file: UploadFile, product_id: str, file_id: str) -> str:
    return _replace_file_raw(file_id, file.file.read(), file.filename, file.content_type)


def replace_subproduct_image(file: UploadFile, subproduct_id: str, file_id: str) -> str:
    return _replace_file_raw(file_id, file.file.read(), file.filename, file.content_type)


def delete_product_image(file_id: str) -> None:
    delete_file(file_id)


def delete_subproduct_image(file_id: str) -> None:
    delete_file(file_id)


def download_product_image(file_id: str) -> tuple[bytes, str]:
    metadata = get_file_metadata(file_id)
    return download_file(file_id), metadata.get("name")


def download_subproduct_image(file_id: str) -> tuple[bytes, str]:
    metadata = get_file_metadata(file_id)
    return download_file(file_id), metadata.get("name")
