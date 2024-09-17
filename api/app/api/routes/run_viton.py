from pydantic import BaseModel
from app.handlers.handlers import MessageHandlerFactory
from fastapi import APIRouter, Request
import json

class VitonSubmitSchema(BaseModel):
    model_upload_id: str
    cloth_upload_id: str

router = APIRouter(prefix="/viton")

@router.post("/submit")
async def viton_submit(
    request: Request,
    message: VitonSubmitSchema
):
    correlation_id = getattr(request.state, 'correlation_id', None)
    message_handler = MessageHandlerFactory(message.message_type)
    cotent_dict = json.loads(message.content)
    await message_handler.handle(cotent_dict, correlation_id)
    return {"status": "Message received", "content": message.content}