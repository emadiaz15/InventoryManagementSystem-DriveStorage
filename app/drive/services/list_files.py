from .client import get_drive_service

def list_files_in_folder(folder_id: str, service=None) -> list[dict]:
    """
    📄 Lista todos los archivos dentro de una carpeta específica de Google Drive.

    Args:
        folder_id: ID de la carpeta en Google Drive que se quiere inspeccionar.
        service: Cliente de Drive, opcional para testeo/mock.

    Returns:
        Lista de diccionarios con metadata básica de cada archivo.
        Cada elemento contiene: id, name, mimeType, createdTime, modifiedTime
    """
    service = service or get_drive_service()  # Si no se inyecta un cliente, lo obtenemos aquí

    # 🔍 Consulta para buscar archivos activos dentro de la carpeta dada
    query = f"'{folder_id}' in parents and trashed=false"

    # 📦 Ejecuta la consulta y devuelve los campos deseados
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id,name,mimeType,createdTime,modifiedTime)'
    ).execute()

    return results.get("files", [])  # Si no hay resultados, devuelve lista vacía
