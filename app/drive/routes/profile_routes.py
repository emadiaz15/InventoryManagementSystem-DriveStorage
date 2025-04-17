import os
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Dict
from app.drive.auth import auth_dependency
from app.drive.uploader import _upload_file_to_folder
from app.drive.config import settings

router = APIRouter(
    prefix="/profile",
    tags=["Profile Image Upload"],
    dependencies=[Depends(auth_dependency)]
)

@router.post("/")
def upload_profile_image_endpoint(
    file: UploadFile = File(...),
    payload: Dict = Depends(auth_dependency)
):
    """
    Sube una imagen de perfil y devuelve el ID del archivo en Drive.
    El nombre del fichero será "<user_id>.<ext>".
    """
    try:
        # Extraer user_id del token JWT
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=400, detail="Token no contiene 'user_id'")

        # Leer bytes y determinar extensión
        data = file.file.read()
        _, ext = os.path.splitext(file.filename)
        filename = f"{user_id}{ext}"

        # Subir directamente al folder de perfiles
        folder_id = settings.PROFILE_IMAGE_FOLDER_ID
        file_id = _upload_file_to_folder(data, filename, file.content_type, folder_id)

        return {"message": "Imagen de perfil subida con éxito", "file_id": file_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir imagen de perfil: {e}")


@router.put("/{file_id}")
def update_profile_image_endpoint(
    file_id: str,
    new_file: UploadFile = File(...),
    payload: Dict = Depends(auth_dependency)
):
    """
    Reemplaza la imagen de perfil existente y retorna el nuevo ID.
    Mantiene el nombre "<user_id>.<ext>".
    """
    try:
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=400, detail="Token no contiene 'user_id'")

        data = new_file.file.read()
        _, ext = os.path.splitext(new_file.filename)
        filename = f"{user_id}{ext}"

        # Reemplazo forzado usando la misma carpeta y override de nombre
        new_id = _upload_file_to_folder(data, filename, new_file.content_type, settings.PROFILE_IMAGE_FOLDER_ID)
        return {"message": "Imagen de perfil actualizada con éxito", "new_file_id": new_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar imagen de perfil: {e}")


@router.get("/{file_id}")
def get_profile_metadata_endpoint(file_id: str):
    """
    Obtiene metadatos de una imagen de perfil en Drive.
    """
    try:
        from app.drive.uploader import get_file_metadata
        metadata = get_file_metadata(file_id)
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener metadatos de la imagen de perfil: {e}")


@router.get("/download/{file_id}")
def download_profile_image_endpoint(file_id: str):
    """
    Descarga la imagen de perfil como archivo adjunto.
    """
    try:
        from app.drive.uploader import download_file
        content = download_file(file_id)
        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file_id}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar imagen de perfil: {e}")
