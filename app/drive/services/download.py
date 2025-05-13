import io
from googleapiclient.http import MediaIoBaseDownload     # 📦 Cliente de descarga de archivos en chunks
from googleapiclient.errors import HttpError             # ❌ Para manejar errores HTTP de la API
from .client import get_drive_service                    # 🔌 Cliente autenticado de Google Drive


def download_file(file_id: str, service=None) -> bytes:
    """
    📥 Descarga un archivo desde Google Drive usando su ID.

    Args:
        file_id: ID único del archivo en Google Drive.
        service: Cliente de Drive (opcional, para testeo/mockeo).

    Returns:
        Contenido binario del archivo.

    Raises:
        FileNotFoundError: Si el archivo no existe (404).
        Otros errores propagados si ocurren durante la descarga.
    """
    service = service or get_drive_service()

    # Solicitud para descargar contenido binario
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)

    try:
        done = False
        while not done:
            _, done = downloader.next_chunk()  # Descarga en chunks si es grande
    except HttpError as e:
        if e.resp.status == 404:
            raise FileNotFoundError(f"Archivo no encontrado: {file_id}")
        raise  # Re-lanza otros errores

    return buffer.getvalue()  # Contenido final en bytes


def get_file_metadata(file_id: str, service=None) -> dict:
    """
    📑 Obtiene metadata de un archivo de Drive (sin descargar su contenido).

    Args:
        file_id: ID del archivo en Drive.
        service: Cliente de Drive (opcional).

    Returns:
        Diccionario con: id, name, mimeType, parents.
    """
    service = service or get_drive_service()

    return service.files().get(
        fileId=file_id,
        fields="id, name, mimeType, parents"  # Solo solicitamos lo que necesitamos
    ).execute()

