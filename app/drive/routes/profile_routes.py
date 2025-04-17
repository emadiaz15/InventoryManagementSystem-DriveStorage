# profile_routes.py
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.drive.auth import auth_dependency
from app.drive.uploader import upload_file, replace_file, get_file_metadata, download_file

router = APIRouter(
    prefix="/profile",
    tags=["Profile Image Upload"],
    dependencies=[Depends(auth_dependency)]
)

@router.post("/")
def upload_profile_image(file: UploadFile = File(...)):
    file_id = upload_file(file, folder_type="profile")
    return {"message": "Imagen de perfil subida con éxito", "file_id": file_id}

@router.put("/{file_id}")
def update_profile_image(
    file_id: str,
    new_file: UploadFile = File(...)
):
    new_id = replace_file(file_id, new_file)
    return {"message": "Imagen de perfil actualizada", "new_file_id": new_id}

@router.get("/{file_id}")
def get_profile_metadata(file_id: str):
    metadata = get_file_metadata(file_id)
    return metadata

@router.get("/download/{file_id}")
def download_profile_image(file_id: str):
    content = download_file(file_id)
    return StreamingResponse(io.BytesIO(content), media_type="application/octet-stream")
