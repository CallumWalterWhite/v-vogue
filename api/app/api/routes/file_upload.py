from typing import Annotated
from fastapi import APIRouter, Depends, File, UploadFile
from app.handlers.message_types import MessageTypes
from app.core.deps import SessionDep
from app.models import OutboundMessage
import json

router = APIRouter()


@router.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@router.post("/uploadfile/")
async def create_upload_file(session:SessionDep, file: UploadFile):
    file_upload_dict = {"filename": file.filename}
    outbound_message = OutboundMessage(content=json.dumps(file_upload_dict), message_type=MessageTypes.UPLOAD_MESSAGE)
    session.add(outbound_message)
    session.commit()
    return {"filename": file.filename}