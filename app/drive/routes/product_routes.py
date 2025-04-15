import os
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from fastapi.responses import JSONResponse, StreamingResponse
from app.drive.auth import verify_jwt_token
from app.drive.uploader import (
    upload_product_image,
    list_product_images,
    replace_product_image,
    download_product_image,
)

router = APIRouter(prefix="/product", tags=["Product Images"])

@router.post("/{product_id}/upload")
async def upload_product_file(
    product_id: str,
    file: UploadFile = File(...),
    x_api_key: str = Header(...)
):
    verify_jwt_token(x_api_key)
    try:
        file_id = upload_product_image(file, product_id)
        return {"message": "Imagen de producto subida con éxito", "file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir la imagen: {str(e)}")


@router.get("/{product_id}/list")
async def list_product_files(
    product_id: str,
    x_api_key: str = Header(...)
):
    verify_jwt_token(x_api_key)
    try:
        images = list_product_images(product_id)
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar imágenes: {str(e)}")


@router.put("/{product_id}/replace/{file_id}")
async def replace_product_file(
    product_id: str,
    file_id: str,
    file: UploadFile = File(...),
    x_api_key: str = Header(...)
):
    verify_jwt_token(x_api_key)
    try:
        updated_id = replace_product_image(file, product_id, file_id)
        return {"message": "Imagen reemplazada exitosamente", "new_file_id": updated_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al reemplazar la imagen: {str(e)}")


@router.get("/{product_id}/download/{file_id}")
async def download_product_file(
    product_id: str,
    file_id: str,
    x_api_key: str = Header(...)
):
    verify_jwt_token(x_api_key)
    try:
        file_bytes, filename = download_product_image(file_id)
        return StreamingResponse(io.BytesIO(file_bytes), media_type="application/octet-stream", headers={
            "Content-Disposition": f"attachment; filename={filename}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar la imagen: {str(e)}")
