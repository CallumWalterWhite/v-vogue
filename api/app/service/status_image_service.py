import json
from typing import Annotated
from fastapi import Depends
from app.handlers.message_types import MessageTypes
from app.models import FileUploadPipeline
from app.core.deps import SessionDep
from app.storage.storage_manager import StorageManager
from app.storage.deps import get_storage_manager
from app.service.message_service import MessageService, get_message_service
from app.service.status_image_service import StatusImageService, get_status_image_service
import uuid

def get_status_image_service(session:SessionDep, status_service: Annotated[StatusImageService, Depends(get_status_image_service)]):
    return StatusImageService(session)

class StatusImageService:
    def __init__(self, session:SessionDep, message_service: Annotated[MessageService, Depends(get_message_service)]):
        self.session = session
        self.storage_manager = storage_manager
        self.message_service = message_service

    def create_image(self, file_path: str, content: bytes, correlation_id:str, image_type: str) -> uuid.UUID:
        new_image_id = uuid.uuid4()
        file_extension = file_path.split(".")[-1] #grr i know this is not a good way
        new_file_name = f"{new_image_id}.{file_extension}"
        self.storage_manager.create_file(new_file_name, content)
        file_upload = FileUpload(id=new_image_id, filename=new_file_name, image_type=type)
        self.session.add(file_upload)
        file_upload_message = {"file_id": str(new_image_id), "type": image_type}
        outbound_message = OutboundMessage(content=json.dumps(file_upload_message), message_type=MessageTypes.UPLOAD_MESSAGE, correlation_id=correlation_id)
        self.message_service.create_message(outbound_message)
        return new_image_id