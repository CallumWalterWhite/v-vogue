from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, UploadFile, Request
from app.service.upload_image_service import get_upload_image_service, UploadImageService

router = APIRouter()

@router.post("/uploadfile/person")
def create_upload_file_person(
    request: Request,
    file: UploadFile,
    upload_image_service: Annotated[UploadImageService, Depends(get_upload_image_service)]
):
    correlation_id = getattr(request.state, 'correlation_id', None)
    
    upload_id: uuid.UUID = upload_image_service.create_image(file.filename, file.file.read(), correlation_id, "person")
    return {"filename": file.filename, "correlation_id": correlation_id, "upload_id": upload_id}

@router.post("/uploadfile/cloth")
def create_upload_file_cloth(
    request: Request,
    file: UploadFile,
    upload_image_service: Annotated[UploadImageService, Depends(get_upload_image_service)]
):
    correlation_id = getattr(request.state, 'correlation_id', None)
    
    upload_id: uuid.UUID = upload_image_service.create_image(file.filename, file.file.read(), correlation_id, "cloth")
    return {"filename": file.filename, "correlation_id": correlation_id, "upload_id": upload_id}