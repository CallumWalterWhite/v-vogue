import json
from typing import Annotated
from fastapi import Depends
from sqlmodel import select
from app.handlers.message_types import MessageTypes
from app.models import OutboundMessage, FileUpload, FileUploadPreProcess
from app.core.deps import SessionDep
from app.storage.storage_manager import StorageManager
from app.storage.deps import get_storage_manager
from app.service.message_service import MessageService, get_message_service
import uuid

def get_upload_image_service(session:SessionDep, storage_manager: Annotated[StorageManager, Depends(get_storage_manager)], message_service: Annotated[MessageService, Depends(get_message_service)]):
    return UploadImageService(session, storage_manager, message_service)

class UploadImageService:
    def __init__(self, session:SessionDep, storage_manager: Annotated[StorageManager, Depends(get_storage_manager)], message_service: Annotated[MessageService, Depends(get_message_service)]):
        self.session = session
        self.storage_manager = storage_manager
        self.message_service = message_service

    def __get_file_upload(self, image_id: uuid.UUID) -> FileUpload:
        file_upload_statement = select(FileUpload).where(FileUpload.id == image_id)
        file_upload: FileUpload = self.session.exec(file_upload_statement).one_or_none()
        if file_upload is None:
            raise Exception("File not found")
        return file_upload

    def create_image(self, file_path: str, content: bytes, correlation_id:str, image_type: str) -> uuid.UUID:
        new_image_id = uuid.uuid4()
        file_extension = file_path.split(".")[-1] #grr i know this is not a good way
        new_file_name = f"{new_image_id}.{file_extension}"
        self.storage_manager.create_file(new_file_name, content)
        file_upload = FileUpload(id=new_image_id, filename=str(new_image_id), fullpath=new_file_name, fileextension=file_extension, image_type=type)
        self.session.add(file_upload)
        file_upload_message = {"file_id": str(new_image_id), "type": image_type}
        outbound_message = OutboundMessage(content=json.dumps(file_upload_message), message_type=MessageTypes.UPLOAD_MESSAGE, correlation_id=correlation_id)
        self.message_service.create_message(outbound_message)
        return new_image_id
    
    def create_image_preprocess(self, orginal_file_upload_id: uuid, name: str, content: bytes, file_extension:str, type: str) -> uuid.UUID:
        file_upload_image: FileUpload = self.__get_file_upload(orginal_file_upload_id)
        new_image_id = uuid.uuid4() # applicaton generated id
        new_file_name = f"{new_image_id}.{file_extension}"
        self.storage_manager.create_file(new_file_name, content)
        file_upload = FileUploadPreProcess(id=new_image_id, orginal_file_upload_id=orginal_file_upload_id, filename=str(new_image_id), fullpath=new_file_name, fileextension=file_extension, type=type)
        self.session.add(file_upload)
        return new_image_id
    
    def get_uploaded_image(self, image_id: uuid.UUID) -> FileUpload:
        return self.__get_file_upload(image_id)
    
    def get_preprocessed_image(self, image_id: uuid.UUID, type: str) -> FileUploadPreProcess:
        file_upload_statement = select(FileUploadPreProcess).where(FileUploadPreProcess.orginal_file_upload_id == image_id and FileUploadPreProcess.type == type)
        file_upload: FileUploadPreProcess = self.session.exec(file_upload_statement).one_or_none()
        if file_upload is None:
            raise Exception("File not found")
        return file_upload