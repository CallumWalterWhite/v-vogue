from typing import Annotated
import uuid
from fastapi import APIRouter, Depends
from app.service.status_image_service import get_status_image_service, StatusImageService

router = APIRouter()

@router.get("/file/{file_id}/status")
def get_file_status(
    file_id: str,
    status_image_service: Annotated[StatusImageService, Depends(get_status_image_service)]
):
    return status_image_service.get_image_status(file_id)