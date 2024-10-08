import json
from typing import Annotated, Generator
from fastapi import Depends
from sqlmodel import select
from app.handlers.message_types import MessageTypes
from app.models import OutboundMessage, FileUpload, FileUploadPreProcess, FileUploadPipeline, PipelineState
from app.core.deps import SessionDep
from app.storage.storage_manager import StorageManager
from app.storage.deps import get_storage_manager
from app.service.message_service import MessageService, get_message_service
from app.service.status_image_service import StatusImageService
import uuid

def get_upload_image_service(session:SessionDep, storage_manager: Annotated[StorageManager, Depends(get_storage_manager)], message_service: Annotated[MessageService, Depends(get_message_service)]):
    return UploadImageService(session, storage_manager, message_service)

class FileUploadDto:
    def __init__(self, 
                 filename: str, 
                 upload_id: uuid.UUID,
                 file_path: str):
        self.filename = filename
        self.upload_id = upload_id
        self.file_path = file_path
        

class UploadImageService:
    def __init__(self, session:SessionDep, storage_manager: Annotated[StorageManager, Depends(get_storage_manager)], message_service: Annotated[MessageService, Depends(get_message_service)]):
        self.session = session
        self.storage_manager = storage_manager
        self.message_service = message_service
        self.status_image_service = StatusImageService(session)

    def __get_file_upload(self, image_id: uuid.UUID) -> FileUpload:
        file_upload_statement = select(FileUpload).where(FileUpload.id == image_id)
        file_upload: FileUpload = self.session.exec(file_upload_statement).one_or_none()
        if file_upload is None:
            raise Exception("File not found")
        return file_upload

    def create_image(self, file_path: str, content: bytes, correlation_id:uuid.UUID, image_type: str) -> uuid.UUID:
        new_image_id = uuid.uuid4()
        
        file_extension = file_path.split(".")[-1] #grr i know this is not a good way
        new_file_name = f"{new_image_id}.{file_extension}"
        
        self.storage_manager.create_file(new_file_name, content)
        file_upload = FileUpload(id=new_image_id, filename=str(new_image_id), fullpath=new_file_name, fileextension=file_extension, image_type=image_type)
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
        file_upload_statement = select(FileUploadPreProcess).where(FileUploadPreProcess.orginal_file_upload_id == image_id).where(FileUploadPreProcess.type == type)
        file_upload: FileUploadPreProcess = self.session.exec(file_upload_statement).one_or_none()
        if file_upload is None:
            raise Exception("File not found")
        return file_upload
    
    def get_all_uploaded_images(self, type:str = 'model', is_completed: bool = False) -> Generator[FileUploadDto, None, None]:
        file_upload_statement = select(FileUpload) \
                                    .where(FileUpload.image_type == type)
        if is_completed:
            file_upload_statement = file_upload_statement \
                                    .join(FileUploadPipeline, FileUploadPipeline.file_upload_id == FileUpload.id, isouter=True) \
                                    .join(PipelineState, PipelineState.pipeline_id == FileUploadPipeline.pipeline_id, isouter=True) \
                                    .where(PipelineState.has_completed == True)                     
        file_uploads: list[FileUpload] = self.session.exec(file_upload_statement).all()
        for file_upload in file_uploads:
            yield FileUploadDto(filename=file_upload.filename, upload_id=file_upload.id, file_path=file_upload.fullpath)

    def get_uploaded_bytes(self, image_id: uuid.UUID) -> bytes:
        file_upload = self.__get_file_upload(image_id)
        return self.storage_manager.get_file(file_upload.fullpath)
        