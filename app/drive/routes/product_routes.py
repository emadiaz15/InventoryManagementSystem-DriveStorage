import io
from app.drive.config import settings
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from app.drive.auth import auth_dependency
from app.drive.uploader import (
    upload_product_image,
    list_product_images,
    get_or_create_subfolder,
    download_product_image,
    delete_product_image,
)

router = APIRouter(
    prefix="/product",
    tags=["Imágenes de Producto"],
    dependencies=[Depends(auth_dependency)]
)

@router.post(
    "/{product_id}/upload",
    summary="Subir imagen de producto",
    description="Sube una imagen al folder correspondiente al producto identificado por `product_id`. "
                "El archivo se almacena en Google Drive bajo una subcarpeta específica.",
    responses={
        200: {"description": "Imagen subida exitosamente"},
        500: {"description": "Error interno al subir la imagen"},
    }
)
async def upload_product_file(
    product_id: str,
    file: UploadFile = File(...)
):
    try:
        file_id = upload_product_image(file, product_id)
        return {"message": "Imagen de producto subida con éxito", "file_id": file_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir la imagen: {e}"
        )


@router.get(
    "/{product_id}/list",
    summary="Listar imágenes del producto",
    description="Devuelve una lista con los metadatos de todas las imágenes asociadas al producto `product_id`. "
                "Incluye nombre de archivo, tipo MIME, fecha de creación, etc.",
    responses={
        200: {"description": "Lista de imágenes devuelta correctamente"},
        500: {"description": "Error al obtener la lista de imágenes"},
    }
)
async def list_product_files(product_id: str):
    try:
        images = list_product_images(product_id)
        return {"images": images}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar imágenes: {e}"
        )


@router.get(
    "/{product_id}/download/{file_id}",
    summary="Descargar imagen de producto",
    description="Permite descargar una imagen específica del producto como archivo adjunto. "
                "Ideal para backup o visualización fuera del sistema.",
    responses={
        200: {"description": "Imagen descargada exitosamente"},
        500: {"description": "Error al descargar la imagen"},
    }
)
async def download_product_file(
    product_id: str,
    file_id: str
):
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


@router.delete(
    "/{product_id}/delete/{file_id}",
    summary="Eliminar imagen de producto",
    description="Elimina permanentemente una imagen del producto del almacenamiento en Google Drive.",
    responses={
        200: {"description": "Imagen eliminada correctamente"},
        500: {"description": "Error al eliminar la imagen"},
    }
)
async def delete_product_file(
    product_id: str,
    file_id: str
):
    try:
        delete_product_image(file_id)
        return {"message": "Imagen eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la imagen: {e}"
        )

@router.post(
    "/{product_id}/create-folder",
    summary="Crear carpeta de producto en Drive",
    description="Crea una carpeta en Google Drive para el producto y devuelve su folder_id.",
)
async def create_product_folder(product_id: str):
    try:
        folder_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID)
        return {"folder_id": folder_id}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear carpeta de producto: {e}"
        )