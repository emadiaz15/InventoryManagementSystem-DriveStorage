import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Header, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from app.drive.auth import verify_jwt_token
from app.drive.uploader import upload_file, replace_file, get_file_metadata, download_file

router = APIRouter(prefix="/profile", tags=["Profile Image Upload"])

# Dependencia para verificar el token JWT en cada endpoint
def auth_dependency(x_api_key: str = Header(...)):
    verify_jwt_token(x_api_key)

@router.post("/", dependencies=[Depends(auth_dependency)])
def upload_profile_image(file: UploadFile = File(...)):
    """
    Sube una imagen de perfil única.
    """
    file_id = upload_file(file, folder_type="profile")
    return {"message": "Imagen de perfil subida con éxito", "file_id": file_id}

@router.put("/{file_id}", dependencies=[Depends(auth_dependency)])
def update_profile_image(file_id: str, new_file: UploadFile = File(...)):
    """
    Reemplaza una imagen de perfil existente.
    """
    new_id = replace_file(file_id, new_file)
    return {"message": "Imagen de perfil actualizada", "new_file_id": new_id}

@router.get("/{file_id}", dependencies=[Depends(auth_dependency)])
def get_profile_metadata(file_id: str):
    """
    Obtiene metadatos de una imagen de perfil.
    """
    metadata = get_file_metadata(file_id)
    return metadata

@router.get("/download/{file_id}", dependencies=[Depends(auth_dependency)])
def download_profile_image(file_id: str):
    """
    Descarga una imagen de perfil.
    """
    content = download_file(file_id)
    return StreamingResponse(io.BytesIO(content), media_type="application/octet-stream")
