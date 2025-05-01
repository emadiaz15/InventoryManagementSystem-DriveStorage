from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.openapi.models import Response as OpenAPIResponse
from typing import Dict
from app.drive.auth import auth_dependency
from app.drive.uploader import (
    _upload_file_to_folder,
    get_file_metadata,
    download_file,
    delete_file 
)
from app.drive.config import settings
import io
import os
from googleapiclient.errors import HttpError

router = APIRouter(
    prefix="/profile",
    tags=["Imagen de Perfil"],
    dependencies=[Depends(auth_dependency)]
)

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.mp4', '.mov', '.avi', '.webm', '.mkv'}

def validate_extension(filename: str):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Extensión de archivo no permitida: {ext}")
    return ext


@router.post("/", summary="Subir imagen de perfil", description="Permite a un usuario autenticado subir una imagen de perfil a Google Drive. El archivo se guarda con el nombre `<user_id>.<ext>` y se retorna el ID asignado.")
def upload_profile_image_endpoint(file: UploadFile = File(...), payload: Dict = Depends(auth_dependency)):
    try:
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=400, detail="Token no contiene 'user_id'")
        data = file.file.read()
        ext = validate_extension(file.filename)
        filename = f"{user_id}{ext}"
        file_id = _upload_file_to_folder(data, filename, file.content_type, settings.PROFILE_IMAGE_FOLDER_ID)
        return {"message": "Imagen de perfil subida con éxito", "file_id": file_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir imagen de perfil: {e}")


@router.put("/{file_id}", summary="Actualizar imagen de perfil", description="Reemplaza una imagen de perfil existente en Google Drive con un nuevo archivo. El nombre del archivo se mantiene como `<user_id>.<ext>`.")
def update_profile_image_endpoint(file_id: str, new_file: UploadFile = File(...), payload: Dict = Depends(auth_dependency)):
    try:
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=400, detail="Token no contiene 'user_id'")
        data = new_file.file.read()
        ext = validate_extension(new_file.filename)
        filename = f"{user_id}{ext}"
        new_id = _upload_file_to_folder(data, filename, new_file.content_type, settings.PROFILE_IMAGE_FOLDER_ID)
        return {"message": "Imagen de perfil actualizada con éxito", "new_file_id": new_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar imagen de perfil: {e}")


@router.get("/download/{file_id}", summary="Descargar imagen de perfil", description="Devuelve el archivo de imagen de perfil como un stream visualizable.")
def download_profile_image_endpoint(file_id: str, payload: Dict = Depends(auth_dependency)):
    try:
        content = download_file(file_id)
        metadata = get_file_metadata(file_id)
        mime_type = metadata.get("mimeType", "image/jpeg")
        return StreamingResponse(io.BytesIO(content), media_type=mime_type, headers={"Content-Disposition": f"inline; filename={file_id}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar imagen de perfil: {e}")


@router.delete("/delete/{file_id}", summary="Eliminar imagen de perfil", description="Elimina el archivo del perfil en Google Drive dado su ID.", responses={
    200: {"description": "Imagen eliminada correctamente"},
    404: {"description": "Archivo no encontrado"},
    500: {"description": "Error inesperado"}
})
def delete_profile_image_endpoint(file_id: str, payload: Dict = Depends(auth_dependency)):
    try:
        delete_file(file_id)
        return {"message": f"Archivo {file_id} eliminado correctamente"}
    except HttpError as e:
        if e.resp.status == 404:
            raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {file_id}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar archivo: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado al eliminar: {e}")
