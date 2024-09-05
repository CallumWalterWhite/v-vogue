import json
from typing import Annotated
from fastapi import Depends
from app.handlers.message_types import MessageTypes
from app.models import OutboundMessage, FileUpload
from app.core.deps import SessionDep
from app.storage.storage_manager import StorageManager
from app.storage.deps import get_storage_manager
import uuid

def get_upload_image_service(session:SessionDep, storage_manager: Annotated[StorageManager, Depends(get_storage_manager)]):
    return UploadImageService(session, storage_manager)

class UploadImageService:
    def __init__(self, session:SessionDep, storage_manager: Annotated[StorageManager, Depends(get_storage_manager)]):
        self.session = session
        self.storage_manager = storage_manager

    def create_image(self, file_path: str, content: bytes, correlation_id:str, type: str):
        new_image_id = uuid.uuid4()
        file_extension = file_path.split(".")[-1] #grr i know this is not a good way
        new_file_name = f"{new_image_id}.{file_extension}"
        self.storage_manager.create_file(new_file_name, content)
        file_upload = FileUpload(id=new_image_id, filename=new_file_name, type=type)
        self.session.add(file_upload)
        file_upload_message = {"file_id": str(new_image_id), "type": type}
        outbound_message = OutboundMessage(content=json.dumps(file_upload_message), message_type=MessageTypes.UPLOAD_MESSAGE, correlation_id=correlation_id)
        self.session.add(outbound_message)
        self.session.commit()
