import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import StreamingResponse

from app.drive.auth import auth_dependency
from app.drive.config import settings

# Servicios
from app.drive.services.upload import prepare_upload, upload_file_to_folder
from app.drive.services.download import download_file, get_file_metadata
from app.drive.services.delete import delete_file
from app.drive.services.folders import get_or_create_subfolder
from app.drive.services.list_files import list_files_in_folder
from app.drive.services.client import get_drive_service

# Validación centralizada
from app.drive.utils.validations import validate_file_extension

router = APIRouter(
    prefix="/product",
    tags=["Imágenes de Producto"],
    dependencies=[Depends(auth_dependency)]
)

@router.post("/{product_id}/upload", summary="Subir imagen de producto")
async def upload_product_file(product_id: str, file: UploadFile = File(...)):
    """
    📤 Sube una imagen a la carpeta específica del producto en Google Drive.
    """
    try:
        # 1. Validación + preparación
        validate_file_extension(file.filename)
        data, _, mimetype = prepare_upload(file)

        # 2. Obtener carpeta del producto
        service = get_drive_service()
        folder_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID, service)

        # 3. Subida al folder
        file_id = upload_file_to_folder(data, file.filename, mimetype, folder_id, service)

        return {"message": "Imagen de producto subida con éxito", "file_id": file_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir la imagen: {str(e)}"
        )

@router.get("/{product_id}/list", summary="Listar imágenes del producto")
async def list_product_files(product_id: str):
    try:
        service = get_drive_service()
        folder_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID, service)
        images = list_files_in_folder(folder_id, service)
        return {"images": images}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar imágenes: {str(e)}"
        )
        
        
@router.get("/{product_id}/download/{file_id}", summary="Descargar imagen de producto")
async def download_product_file(product_id: str, file_id: str, _: dict = Depends(auth_dependency)):
    try:
        service = get_drive_service()
        expected_folder_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID, service)

        metadata = get_file_metadata(file_id, service)
        parents = metadata.get("parents") or []

        if expected_folder_id not in parents:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Archivo no pertenece al producto {product_id}"
            )

        data = download_file(file_id, service)
        mime_type = metadata.get("mimeType", "application/octet-stream")
        filename = metadata.get("name")

        return StreamingResponse(
            io.BytesIO(data),
            media_type=mime_type,
            headers={"Content-Disposition": f'inline; filename="{filename}"'}
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo no encontrado en Google Drive")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado al descargar archivo: {str(e)}")


@router.delete("/{product_id}/delete/{file_id}", summary="Eliminar imagen de producto")
async def delete_product_file(product_id: str, file_id: str):
    try:
        delete_file(file_id)
        return {"message": "Imagen eliminada exitosamente"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la imagen: {str(e)}"
        )
