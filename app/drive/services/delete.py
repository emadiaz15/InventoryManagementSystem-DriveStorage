from .client import get_drive_service

def delete_file(file_id: str, service=None):
    """
    🗑️ Elimina un archivo de Google Drive por su ID.

    Args:
        file_id: ID del archivo a eliminar.
        service: Cliente de Google Drive (opcional para test/mock).

    Returns:
        None. Si tiene éxito, el archivo es eliminado de Drive.
    
    Raises:
        HttpError: Si el archivo no existe o hay un problema con la API.
    """
    service = service or get_drive_service()  # Usa cliente inyectado o genera uno nuevo

    # Ejecuta la operación de borrado
    service.files().delete(fileId=file_id).execute()
