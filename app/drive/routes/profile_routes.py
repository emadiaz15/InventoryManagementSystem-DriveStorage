import io
from typing import Dict

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from googleapiclient.errors import HttpError

from app.drive.auth import auth_dependency                          # 🔐 Dependencia para validar JWT
from app.drive.config import settings                               # ⚙️ Configuración de carpetas, claves, etc.

# 🧱 Servicios desacoplados
from app.drive.services.upload import validate_file_extension, prepare_upload, upload_file_to_folder
from app.drive.services.update import replace_file
from app.drive.services.download import download_file, get_file_metadata
from app.drive.services.delete import delete_file

# 📦 Inicializa el router para imágenes de perfil
router = APIRouter(
    prefix="/profile",
    tags=["Imagen de Perfil"]
)

# 🎯 Generador del nombre de archivo de perfil
def get_profile_filename(user_id: str, ext: str) -> str:
    return f"{user_id}{ext}"

@router.post(
    "/",
    summary="Subir imagen de perfil"
)
def upload_profile_image(
    file: UploadFile = File(...),
    payload: Dict = Depends(auth_dependency)
):
    """
    📤 Sube una imagen de perfil a la carpeta predefinida en Google Drive.
    El nombre del archivo será el ID del usuario + extensión.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token no contiene 'user_id'")

    try:
        ext = validate_file_extension(file.filename)           # Verifica que la extensión esté permitida
        filename = get_profile_filename(user_id, ext)          # Genera nombre único basado en user_id
        data, _, mimetype = prepare_upload(file)               # Extrae binarios + MIME

        file_id = upload_file_to_folder(
            data, filename, mimetype, settings.PROFILE_IMAGE_FOLDER_ID
        )

        return {"message": "Imagen de perfil subida con éxito", "file_id": file_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir imagen de perfil: {str(e)}")


@router.put(
    "/{file_id}",
    summary="Actualizar imagen de perfil"
)
def update_profile_image(
    file_id: str,
    new_file: UploadFile = File(...),
    payload: Dict = Depends(auth_dependency)
):
    """
    🔁 Reemplaza la imagen de perfil existente en Google Drive manteniendo el mismo ID.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token no contiene 'user_id'")

    try:
        ext = validate_file_extension(new_file.filename)
        filename = get_profile_filename(user_id, ext)

        # Usa el servicio desacoplado para reemplazo
        new_id = replace_file(file_id, new_file, filename)

        return {"message": "Imagen de perfil actualizada con éxito", "new_file_id": new_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar imagen: {str(e)}")


@router.get(
    "/download/{file_id}",
    summary="Descargar imagen de perfil"
)
def download_profile_image(
    file_id: str,
    payload: Dict = Depends(auth_dependency)
):
    """
    📥 Descarga una imagen de perfil desde Google Drive.
    """
    try:
        content = download_file(file_id)                           # Descarga binaria
        metadata = get_file_metadata(file_id)                      # Info: nombre, MIME, etc.
        mime_type = metadata.get("mimeType", "application/octet-stream")

        return StreamingResponse(
            io.BytesIO(content),
            media_type=mime_type,
            headers={"Content-Disposition": f"inline; filename={file_id}"}
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {file_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar imagen: {str(e)}")


@router.delete(
    "/delete/{file_id}",
    summary="Eliminar imagen de perfil"
)
def delete_profile_image(
    file_id: str,
    payload: Dict = Depends(auth_dependency)
):
    """
    🗑️ Elimina una imagen de perfil de Google Drive.
    """
    try:
        delete_file(file_id)
        return {"message": f"Archivo {file_id} eliminado correctamente"}

    except HttpError as e:
        if e.resp.status == 404:
            raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {file_id}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar archivo: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado al eliminar: {str(e)}")
