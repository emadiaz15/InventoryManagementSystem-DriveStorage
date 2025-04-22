import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from app.drive.auth import auth_dependency
from app.drive.uploader import (
    upload_subproduct_image,
    list_subproduct_images,
    replace_subproduct_image,
    download_subproduct_image,
    delete_subproduct_image,
)

router = APIRouter(
    prefix="/subproduct",
    tags=["Imágenes de Subproducto"],
    dependencies=[Depends(auth_dependency)]
)

@router.post(
    "/{product_id}/{subproduct_id}/upload",
    summary="Subir imagen de subproducto",
    description="Sube una imagen al folder específico del subproducto asociado al `product_id`. "
                "La imagen se organiza jerárquicamente bajo su producto padre.",
    responses={
        200: {"description": "Imagen de subproducto subida exitosamente"},
        500: {"description": "Error interno al subir la imagen"},
    }
)
async def upload_subproduct_file(
    product_id: str,
    subproduct_id: str,
    file: UploadFile = File(...)
):
    try:
        file_id = upload_subproduct_image(file, subproduct_id, product_id)
        return {"message": "Imagen de subproducto subida con éxito", "file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al subir la imagen: {e}")


@router.get(
    "/{product_id}/{subproduct_id}/list",
    summary="Listar imágenes de subproducto",
    description="Devuelve una lista con los metadatos de todas las imágenes asociadas al `subproduct_id`, "
                "organizadas dentro del folder del `product_id` correspondiente.",
    responses={
        200: {"description": "Lista de imágenes obtenida correctamente"},
        500: {"description": "Error al obtener la lista de imágenes"},
    }
)
async def list_subproduct_files(
    product_id: str,
    subproduct_id: str
):
    try:
        images = list_subproduct_images(subproduct_id, product_id)
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al listar imágenes: {e}")


@router.put(
    "/{product_id}/{subproduct_id}/replace/{file_id}",
    summary="Reemplazar imagen de subproducto",
    description="Reemplaza una imagen ya existente de un subproducto, usando su `file_id` como referencia.",
    responses={
        200: {"description": "Imagen reemplazada exitosamente"},
        500: {"description": "Error al reemplazar la imagen"},
    }
)
async def replace_subproduct_file(
    product_id: str,
    subproduct_id: str,
    file_id: str,
    file: UploadFile = File(...)
):
    try:
        new_id = replace_subproduct_image(file, subproduct_id, file_id)
        return {"message": "Imagen reemplazada exitosamente", "new_file_id": new_id}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al reemplazar la imagen: {e}")


@router.get(
    "/{product_id}/{subproduct_id}/download/{file_id}",
    summary="Descargar imagen de subproducto",
    description="Descarga una imagen específica asociada al `subproduct_id`, retornándola como archivo adjunto.",
    responses={
        200: {"description": "Imagen descargada exitosamente"},
        500: {"description": "Error al descargar la imagen"},
    }
)
async def download_subproduct_file(
    product_id: str,
    subproduct_id: str,
    file_id: str
):
    try:
        data, filename = download_subproduct_image(file_id)
        return StreamingResponse(
            io.BytesIO(data),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al descargar la imagen: {e}")


@router.delete(
    "/{product_id}/{subproduct_id}/delete/{file_id}",
    summary="Eliminar imagen de subproducto",
    description="Elimina una imagen específica del subproducto desde el almacenamiento en Drive.",
    responses={
        200: {"description": "Imagen eliminada correctamente"},
        500: {"description": "Error al eliminar la imagen"},
    }
)
async def delete_subproduct_file(
    product_id: str,
    subproduct_id: str,
    file_id: str
):
    try:
        delete_subproduct_image(file_id)
        return {"message": "Imagen eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar la imagen: {e}")
