from .client import get_drive_service

def get_or_create_subfolder(name: str, parent_id: str, service=None) -> str:
    """
    📁 Busca una subcarpeta por nombre dentro de una carpeta padre. Si no existe, la crea.

    Args:
        name: Nombre de la subcarpeta a buscar/crear.
        parent_id: ID de la carpeta contenedora (padre).
        service: Cliente de Google Drive (opcional para inyección).

    Returns:
        El ID de la subcarpeta existente o recién creada.
    """
    service = service or get_drive_service()

    # 🔍 Consulta para buscar una carpeta con ese nombre dentro del padre
    query = (
        f"name='{name}' and '{parent_id}' in parents and "
        "mimeType='application/vnd.google-apps.folder' and trashed=false"
    )

    result = service.files().list(q=query, fields="files(id)").execute()
    folders = result.get("files", [])

    # ✅ Si ya existe, devuelve su ID
    if folders:
        return folders[0]["id"]

    # 🚀 Si no existe, crea la subcarpeta
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }

    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]

def get_subfolder_id(name: str, parent_id: str, service=None) -> str | None:
    """
    🔎 Busca el ID de una subcarpeta sin crearla si no existe.

    Args:
        name: Nombre de la subcarpeta a buscar.
        parent_id: ID de la carpeta contenedora (padre).
        service: Cliente de Google Drive (opcional para inyección).

    Returns:
        El ID de la carpeta si se encuentra, o None si no existe.
    """
    service = service or get_drive_service()

    query = (
        f"name='{name}' and '{parent_id}' in parents and "
        "mimeType='application/vnd.google-apps.folder' and trashed=false"
    )

    result = service.files().list(q=query, fields="files(id)").execute()
    folders = result.get("files", [])

    # Devuelve el ID si hay resultados; de lo contrario, None
    return folders[0]["id"] if folders else None
