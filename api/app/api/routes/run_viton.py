from typing import Annotated
import uuid
from pydantic import BaseModel
from app.handlers.handlers import MessageHandlerFactory
from fastapi import APIRouter, Depends, Request
from app.service.viton_service import get_viton_image_service, VitonImageService
import json

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