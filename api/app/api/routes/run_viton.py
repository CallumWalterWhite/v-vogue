from typing import Annotated
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Request, Response
from app.service.viton_service import get_viton_image_service, VitonImageService
from app.service.status_image_service import get_status_image_service, StatusImageService

class VitonSubmitSchema(BaseModel):
    model_upload_id: uuid.UUID
    cloth_upload_id: uuid.UUID

router = APIRouter(prefix="/viton")

@router.post("/submit")
async def viton_submit(
    request: Request,
    message: VitonSubmitSchema,
    viton_image_service: Annotated[VitonImageService, Depends(get_viton_image_service)]
):
    correlation_id = getattr(request.state, 'correlation_id', None)
    
    upload_id: uuid.UUID = viton_image_service.create_viton_image(message.model_upload_id, message.cloth_upload_id, correlation_id)
    return {"correlation_id": correlation_id, "upload_id": upload_id}

@router.get("/{image_id}/status/")
async def viton_status(
    image_id: uuid.UUID,
    status_image_service: Annotated[StatusImageService, Depends(get_status_image_service)]
):
    return status_image_service.get_image_status(image_id)

@router.get("/outputs")
async def viton_outputs(
    viton_image_service: Annotated[VitonImageService, Depends(get_viton_image_service)],
    is_completed: bool = False
):
    return viton_image_service.get_all_viton_images(is_completed)

@router.get("/{image_id}/show")
async def viton_show(
    image_id: uuid.UUID,
    viton_image_service: Annotated[VitonImageService, Depends(get_viton_image_service)]
):
    uploaded_bytes: bytes = viton_image_service.get_image_bytes(image_id)
    return Response(content=uploaded_bytes, media_type="image/png")