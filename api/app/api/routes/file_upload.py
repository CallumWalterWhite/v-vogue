from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile
from app.storage.storage_manager import StorageManager
from app.service.upload_image_service import get_upload_image_service

router = APIRouter()

@router.post("/uploadfile/")
async def create_upload_file(file: UploadFile, upload_image_service: Annotated[StorageManager, Depends(get_upload_image_service)]):
    upload_image_service.create_image(file.filename, file.file.read())
    return {"filename": file.filename}