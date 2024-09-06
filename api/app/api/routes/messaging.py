from pydantic import BaseModel
from app.handlers.handlers import MessageHandlerFactory
from app.core.messaging.publisher import SendMessageSchema
from fastapi import APIRouter
import json

class InboundMessageSchema(BaseModel):
    content: str | None
    message_type: str
    correlation_id: str | None = None

router = APIRouter(prefix="/message")

@router.post("/inbox")
async def receive_message(message: InboundMessageSchema):
    message_handler = MessageHandlerFactory(message.message_type)
    cotent_dict = json.loads(message.content)
    await message_handler.handle(cotent_dict)
    return {"status": "Message received", "content": message.content}