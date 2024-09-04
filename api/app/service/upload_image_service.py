import json
from typing import Annotated
from fastapi import Depends
from app.handlers.message_types import MessageTypes
from app.models import OutboundMessage, FileUpload
from app.core.deps import SessionDep
from app.storage.storage_manager import StorageManager
from app.storage.deps import get_storage_manager

def get_upload_image_service(session:SessionDep, storage_manager: Annotated[StorageManager, Depends(get_storage_manager)]):
    return UploadImageService(session, storage_manager)

class UploadImageService:
    def __init__(self, session:SessionDep, storage_manager: Annotated[StorageManager, Depends(get_storage_manager)]):
        self.session = session
        self.storage_manager = storage_manager

    def create_image(self, file_path: str, content: bytes):
        self.storage_manager.create_file(file_path, content)
        file_upload = FileUpload(filename=file_path)
        self.session.add(file_upload)
        self.session.commit()
        self.session.refresh(file_upload)
        file_upload_message = {"file_id": str(file_upload.id)}
        outbound_message = OutboundMessage(content=json.dumps(file_upload_message), message_type=MessageTypes.UPLOAD_MESSAGE)
        self.session.add(outbound_message)
        self.session.commit()