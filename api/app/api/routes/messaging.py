from app.handlers import InboundMessageSchema, MessageHandlerFactory
from typing import Annotated
from fastapi import APIRouter, Depends, File, UploadFile

router = APIRouter()

@router.post("/inbox/")
async def receive_message(message: InboundMessageSchema):
    # Add message to inbox
    MessageHandlerFactory(message.HANDLER_NAME).handle(message.CONTENT)
    return {"status": "Message received", "content": InboundMessageSchema.content}