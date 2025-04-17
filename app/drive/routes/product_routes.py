# product_routes.py
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from app.drive.auth import auth_dependency
from app.drive.uploader import (
    upload_product_image,
    list_product_images,
    replace_product_image,
    download_product_image,
    delete_product_image,
)

router = APIRouter(
    prefix="/product",
    tags=["Product Images"],
    dependencies=[Depends(auth_dependency)]
)

@router.post("/{product_id}/upload")
async def upload_product_file(
    product_id: str,
    file: UploadFile = File(...)
):
    """
    Sube una imagen de producto a la carpeta del ID especificado.
    """
    try:
        file_id = upload_product_image(file, product_id)
        return {"message": "Imagen de producto subida con éxito", "file_id": file_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir la imagen: {e}"
        )

@router.get("/{product_id}/list")
async def list_product_files(product_id: str):
    """
    Lista todas las imágenes de producto existentes en la carpeta del ID.
    """
    try:
        images = list_product_images(product_id)
        return {"images": images}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar imágenes: {e}"
        )

@router.put("/{product_id}/replace/{file_id}")
async def replace_product_file(
    product_id: str,
    file_id: str,
    file: UploadFile = File(...)
):
    """
    Reemplaza una imagen existente por una nueva en la carpeta de producto.
    """
    try:
        new_id = replace_product_image(file, product_id, file_id)
        return {"message": "Imagen reemplazada exitosamente", "new_file_id": new_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al reemplazar la imagen: {e}"
        )

@router.get("/{product_id}/download/{file_id}")
async def download_product_file(
    product_id: str,
    file_id: str
):
    """
    Descarga la imagen especificada como un archivo adjunto.
    """
    try:
        data, filename = download_product_image(file_id)
        return StreamingResponse(
            io.BytesIO(data),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al descargar la imagen: {e}"
        )

@router.delete("/{product_id}/delete/{file_id}")
async def delete_product_file(
    product_id: str,
    file_id: str
):
    """
    Elimina la imagen especificada del almacenamiento.
    """
    try:
        delete_product_image(file_id)
        return {"message": "Imagen eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la imagen: {e}"
        )
