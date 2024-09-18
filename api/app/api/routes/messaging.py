import uuid
from pydantic import BaseModel
from app.handlers.handlers import MessageHandlerFactory
from fastapi import APIRouter, Request
import json

class InboundMessageSchema(BaseModel):
    content: str | None
    message_type: str
    correlation_id: str | None = None

router = APIRouter(prefix="/message")

@router.post("/inbox")
async def receive_message(
    request: Request,
    message: InboundMessageSchema
):
    correlation_id = getattr(request.state, 'correlation_id', None)
    message_handler = MessageHandlerFactory(message.message_type)
    cotent_dict = json.loads(message.content)
    await message_handler.handle(cotent_dict, correlation_id)
    return {"status": "Message received", "content": message.content}