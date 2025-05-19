import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import StreamingResponse

from app.drive.auth import auth_dependency
from app.drive.config import settings

from app.drive.services.upload import prepare_upload, upload_file_to_folder
from app.drive.services.update import replace_file
from app.drive.services.download import download_file, get_file_metadata
from app.drive.services.delete import delete_file
from app.drive.services.folders import get_or_create_subfolder
from app.drive.services.list_files import list_files_in_folder
from app.drive.services.client import get_drive_service

from app.drive.utils.validations import validate_file_extension

router = APIRouter(
    prefix="/subproduct",
    tags=["Imágenes de Subproducto"],
    dependencies=[Depends(auth_dependency)]
)

@router.post("/{product_id}/{subproduct_id}/upload", summary="Subir imagen de subproducto")
async def upload_subproduct_file(product_id: str, subproduct_id: str, file: UploadFile = File(...),_: dict = Depends(auth_dependency)
):
    """
    📤 Sube una imagen a /PRODUCT_ID/SUBPRODUCT_ID/ en Google Drive.
    """
    try:
        validate_file_extension(file.filename)
        data, _, mimetype = prepare_upload(file)

        service = get_drive_service()

        # 📁 Crear carpeta del producto si no existe
        product_folder = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID, service)

        # 📁 Crear subcarpeta del subproducto dentro del producto
        subproduct_folder = get_or_create_subfolder(subproduct_id, product_folder, service)

        # 🚀 Subir al subfolder
        file_id = upload_file_to_folder(data, file.filename, mimetype, subproduct_folder, service)

        return {"message": "Imagen de subproducto subida con éxito", "file_id": file_id}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir la imagen: {str(e)}"
        )

@router.get("/{product_id}/{subproduct_id}/list", summary="Listar imágenes de subproducto")
async def list_subproduct_files(
    product_id: str,
    subproduct_id: str,
    _: dict = Depends(auth_dependency)
):
    try:
        service = get_drive_service()
        product_folder = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID, service)
        sub_folder = get_or_create_subfolder(subproduct_id, product_folder, service)

        images = list_files_in_folder(sub_folder, service)
        return {"images": images}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar imágenes: {str(e)}"
        )


@router.put("/{product_id}/{subproduct_id}/replace/{file_id}", summary="Reemplazar imagen de subproducto")
async def replace_subproduct_file(
    product_id: str,
    subproduct_id: str,
    file_id: str,
    file: UploadFile = File(...),
    _: dict = Depends(auth_dependency)
):
    try:
        service = get_drive_service()
        product_folder_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID, service)
        subproduct_folder_id = get_or_create_subfolder(subproduct_id, product_folder_id, service)

        metadata = get_file_metadata(file_id, service)
        if subproduct_folder_id not in metadata.get("parents", []):
            raise HTTPException(403, detail="El archivo no pertenece al subproducto indicado.")

        ext = validate_file_extension(file.filename)
        filename = f"{subproduct_id}{ext}"

        new_id = replace_file(file_id, file, filename)
        return {"message": "Imagen reemplazada exitosamente", "new_file_id": new_id}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al reemplazar la imagen: {str(e)}"
        )


@router.get("/{product_id}/{subproduct_id}/download/{file_id}", summary="Descargar imagen de subproducto")
async def download_subproduct_file(product_id: str, subproduct_id: str, file_id: str, _: dict = Depends(auth_dependency)
):
    try:
        service = get_drive_service()

        # Validar jerarquía de carpetas
        product_folder_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID, service)
        subproduct_folder_id = get_or_create_subfolder(subproduct_id, product_folder_id, service)

        metadata = get_file_metadata(file_id, service)
        parents = metadata.get("parents", [])

        if subproduct_folder_id not in parents:
            raise HTTPException(status_code=404, detail="Archivo no pertenece a este subproducto")

        content = download_file(file_id, service)
        mime_type = metadata.get("mimeType", "application/octet-stream")
        filename = metadata.get("name")

        return StreamingResponse(
            io.BytesIO(content),
            media_type=mime_type,
            headers={"Content-Disposition": f'inline; filename="{filename}"'}
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo no encontrado en Google Drive")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al descargar la imagen: {str(e)}"
        )

@router.delete("/{product_id}/{subproduct_id}/delete/{file_id}", summary="Eliminar imagen de subproducto")
async def delete_subproduct_file(
    product_id: str,
    subproduct_id: str,
    file_id: str,
    _: dict = Depends(auth_dependency)
):
    try:
        service = get_drive_service()
        product_folder_id = get_or_create_subfolder(product_id, settings.PRODUCTS_IMAGE_FOLDER_ID, service)
        subproduct_folder_id = get_or_create_subfolder(subproduct_id, product_folder_id, service)

        metadata = get_file_metadata(file_id, service)
        if subproduct_folder_id not in metadata.get("parents", []):
            raise HTTPException(status_code=403, detail="Archivo no pertenece a este subproducto")

        delete_file(file_id)
        return {"message": "Imagen eliminada exitosamente"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar la imagen: {str(e)}"
        )