import io
from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from .config import settings


def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_SERVICE_ACCOUNT_JSON,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=credentials)


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


def replace_file(file_id: str, new_file_data: bytes, new_filename: str, mimetype: str):
    service = get_drive_service()

    media = MediaIoBaseUpload(io.BytesIO(new_file_data), mimetype=mimetype, resumable=True)

    updated_file = service.files().update(
        fileId=file_id,
        media_body=media,
        body={"name": new_filename}
    ).execute()

    return updated_file.get("id")


def get_file_metadata(file_id: str) -> dict:
    service = get_drive_service()
    metadata = service.files().get(fileId=file_id).execute()
    return metadata


def download_file(file_id: str) -> bytes:
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    return file_data.getvalue()
