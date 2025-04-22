from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.openapi.models import Response as OpenAPIResponse
from typing import Dict
from app.drive.auth import auth_dependency
from app.drive.uploader import (
    _upload_file_to_folder,
    get_file_metadata,
    download_file,
)
from app.drive.config import settings
import io
import os

router = APIRouter(
    prefix="/profile",
    tags=["Imagen de Perfil"],
    dependencies=[Depends(auth_dependency)]
)

@router.post(
    "/",
    summary="Subir imagen de perfil",
    description="Permite a un usuario autenticado subir una imagen de perfil a Google Drive. "
                "El archivo se guarda con el nombre `<user_id>.<ext>` y se retorna el ID asignado.",
    responses={
        200: {"description": "Imagen subida con éxito"},
        400: {"description": "Falta el user_id o error de validación"},
        500: {"description": "Error en el servidor o con Drive"},
    }
)
def upload_profile_image_endpoint(
    file: UploadFile = File(...),
    payload: Dict = Depends(auth_dependency)
):
    try:
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=400, detail="Token no contiene 'user_id'")

        data = file.file.read()
        _, ext = os.path.splitext(file.filename)
        filename = f"{user_id}{ext}"
        file_id = _upload_file_to_folder(data, filename, file.content_type, settings.PROFILE_IMAGE_FOLDER_ID)

        return {"message": "Imagen de perfil subida con éxito", "file_id": file_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir imagen de perfil: {e}")


@router.put(
    "/{file_id}",
    summary="Actualizar imagen de perfil",
    description="Reemplaza una imagen de perfil existente en Google Drive con un nuevo archivo. "
                "El nombre del archivo se mantiene como `<user_id>.<ext>`.",
    responses={
        200: {"description": "Imagen reemplazada exitosamente"},
        400: {"description": "Token inválido o falta user_id"},
        500: {"description": "Error al reemplazar la imagen"},
    }
)
def update_profile_image_endpoint(
    file_id: str,
    new_file: UploadFile = File(...),
    payload: Dict = Depends(auth_dependency)
):
    try:
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=400, detail="Token no contiene 'user_id'")

        data = new_file.file.read()
        _, ext = os.path.splitext(new_file.filename)
        filename = f"{user_id}{ext}"
        new_id = _upload_file_to_folder(data, filename, new_file.content_type, settings.PROFILE_IMAGE_FOLDER_ID)
        return {"message": "Imagen de perfil actualizada con éxito", "new_file_id": new_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar imagen de perfil: {e}")


@router.get(
    "/{file_id}",
    summary="Obtener metadatos de imagen de perfil",
    description="Obtiene información (metadatos) sobre una imagen de perfil almacenada en Drive, "
                "como nombre de archivo, tipo MIME, fecha de creación, etc.",
    responses={
        200: {"description": "Metadatos devueltos exitosamente"},
        500: {"description": "Error al recuperar los metadatos"},
    }
)
def get_profile_metadata_endpoint(file_id: str):
    try:
        metadata = get_file_metadata(file_id)
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener metadatos de la imagen de perfil: {e}")


@router.get(
    "/download/{file_id}",
    summary="Descargar imagen de perfil",
    description="Devuelve el archivo de imagen de perfil como un stream visualizable. "
                "Ideal para previsualizar o cargar el avatar del usuario.",
    responses={
        200: {"description": "Imagen devuelta exitosamente como stream"},
        500: {"description": "Error al descargar la imagen"},
    }
)
def download_profile_image_endpoint(file_id: str):
    try:
        content = download_file(file_id)
        metadata = get_file_metadata(file_id)
        mime_type = metadata.get("mimeType", "image/jpeg")
        return StreamingResponse(
            io.BytesIO(content),
            media_type=mime_type,
            headers={"Content-Disposition": f"inline; filename={file_id}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar imagen de perfil: {e}")
