from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Response, UploadFile, Request
from app.service.upload_image_service import get_upload_image_service, UploadImageService

router = APIRouter()

@router.post("/uploadfile/person")
def create_upload_file_person(
    request: Request,
    file: UploadFile,
    upload_image_service: Annotated[UploadImageService, Depends(get_upload_image_service)]
):
    correlation_id = getattr(request.state, 'correlation_id', None)
    
    upload_id: uuid.UUID = upload_image_service.create_image(file.filename, file.file.read(), correlation_id, "model")
    return {"filename": file.filename, "correlation_id": correlation_id, "upload_id": upload_id}

@router.post("/uploadfile/garment")
def create_upload_file_cloth(
    request: Request,
    file: UploadFile,
    upload_image_service: Annotated[UploadImageService, Depends(get_upload_image_service)]
):
    correlation_id = getattr(request.state, 'correlation_id', None)
    
    upload_id: uuid.UUID = upload_image_service.create_image(file.filename, file.file.read(), correlation_id, "cloth")
    return {"filename": file.filename, "correlation_id": correlation_id, "upload_id": upload_id}

@router.get("/uploadfile/models")
def get_all_model_images(
    upload_image_service: Annotated[UploadImageService, Depends(get_upload_image_service)],
    is_completed: bool = False
):
    return upload_image_service.get_all_uploaded_images('model', is_completed)

@router.get("/uploadfile/garments")
def get_all_model_images(
    upload_image_service: Annotated[UploadImageService, Depends(get_upload_image_service)],
    is_completed: bool = False
):
    return upload_image_service.get_all_uploaded_images('cloth', is_completed)

@router.get("/uploadfile/{image_id}/show")
def get_image(
    image_id: uuid.UUID,
    upload_image_service: Annotated[UploadImageService, Depends(get_upload_image_service)]
):
    uploaded_bytes: bytes = upload_image_service.get_uploaded_bytes(image_id)
    return Response(content=uploaded_bytes, media_type="image/png")