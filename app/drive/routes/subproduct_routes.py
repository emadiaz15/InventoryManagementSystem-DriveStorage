import os
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from fastapi.responses import JSONResponse, StreamingResponse
from app.drive.auth import verify_jwt_token
from app.drive.uploader import (
    upload_subproduct_image,
    list_subproduct_images,
    replace_subproduct_image,
    download_subproduct_image,
    delete_drive_file,
)

router = APIRouter(prefix="/subproduct", tags=["Subproduct Images"])

@router.post("/{subproduct_id}/upload")
async def upload_subproduct_file(
    subproduct_id: str,
    file: UploadFile = File(...),
    x_api_key: str = Header(...),
    product_id: str = Header(...)
):
    verify_jwt_token(x_api_key)
    try:
        file_id = upload_subproduct_image(file, subproduct_id, product_id)
        return {"message": "Imagen de subproducto subida con éxito", "file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir la imagen: {str(e)}")

@router.get("/{subproduct_id}/list")
async def list_subproduct_files(
    subproduct_id: str,
    x_api_key: str = Header(...),
    product_id: str = Header(...)
):
    verify_jwt_token(x_api_key)
    try:
        images = list_subproduct_images(subproduct_id, product_id)
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar imágenes: {str(e)}")

@router.put("/{subproduct_id}/replace/{file_id}")
async def replace_subproduct_file(
    subproduct_id: str,
    file_id: str,
    file: UploadFile = File(...),
    x_api_key: str = Header(...)
):
    verify_jwt_token(x_api_key)
    try:
        updated_id = replace_subproduct_image(file, subproduct_id, file_id)
        return {"message": "Imagen reemplazada exitosamente", "new_file_id": updated_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al reemplazar la imagen: {str(e)}")

@router.get("/{subproduct_id}/download/{file_id}")
async def download_subproduct_file(
    subproduct_id: str,
    file_id: str,
    x_api_key: str = Header(...)
):
    verify_jwt_token(x_api_key)
    try:
        file_bytes, filename = download_subproduct_image(file_id)
        return StreamingResponse(io.BytesIO(file_bytes), media_type="application/octet-stream", headers={
            "Content-Disposition": f"attachment; filename={filename}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar la imagen: {str(e)}")

@router.delete("/{subproduct_id}/delete/{file_id}")
async def delete_subproduct_file(
    subproduct_id: str,
    file_id: str,
    x_api_key: str = Header(...)
):
    verify_jwt_token(x_api_key)
    try:
        delete_drive_file(file_id)
        return {"message": "Imagen eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar la imagen: {str(e)}")
