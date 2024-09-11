from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, UploadFile, Request
from app.storage.storage_manager import StorageManager
from app.service.upload_image_service import get_upload_image_service

router = APIRouter()

@router.get("/file/{file_id}/status")
def get_file_status(
    file_id: uuid.UUID,
    upload_image_service: Annotated[StorageManager, Depends(get_upload_image_service)]
):
    return upload_image_service.get_file_status(file_id)