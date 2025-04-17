import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
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
    tags=["Subproduct Images"],
    dependencies=[Depends(auth_dependency)]
)

@router.post("/{product_id}/{subproduct_id}/upload")
async def upload_subproduct_file(
    product_id: str,
    subproduct_id: str,
    file: UploadFile = File(...)
):
    try:
        file_id = upload_subproduct_image(file, subproduct_id, product_id)
        return {"message": "Imagen de subproducto subida con éxito", "file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir la imagen: {e}")

@router.get("/{product_id}/{subproduct_id}/list")
async def list_subproduct_files(
    product_id: str,
    subproduct_id: str
):
    try:
        images = list_subproduct_images(subproduct_id, product_id)
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar imágenes: {e}")

@router.put("/{product_id}/{subproduct_id}/replace/{file_id}")
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
        raise HTTPException(status_code=500, detail=f"Error al reemplazar la imagen: {e}")

@router.get("/{product_id}/{subproduct_id}/download/{file_id}")
async def download_subproduct_file(
    product_id: str,
    subproduct_id: str,
    file_id: str
):
    try:
        data, filename = download_subproduct_image(file_id)
        return StreamingResponse(io.BytesIO(data),
                                 media_type="application/octet-stream",
                                 headers={"Content-Disposition": f"attachment; filename={filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar la imagen: {e}")

@router.delete("/{product_id}/{subproduct_id}/delete/{file_id}")
async def delete_subproduct_file(
    product_id: str,
    subproduct_id: str,
    file_id: str
):
    try:
        delete_subproduct_image(file_id)
        return {"message": "Imagen eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar la imagen: {e}")
