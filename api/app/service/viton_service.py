import json
from typing import Annotated
from fastapi import Depends
from sqlmodel import select
from app.storage.deps import get_storage_manager
from app.storage.storage_manager import StorageManager
from app.handlers.message_types import MessageTypes
from app.models import OutboundMessage, VitonUploadImage
from app.core.deps import SessionDep
from app.service.message_service import MessageService, get_message_service
import uuid

def get_viton_image_service(session:SessionDep, message_service: Annotated[MessageService, Depends(get_message_service)], storage_manager: Annotated[StorageManager, Depends(get_storage_manager)]):
    return VitonImageService(session, message_service, storage_manager)

class VitonUploadImageDto():
    def __init__(self, 
                 filename: str, 
                 upload_id: uuid.UUID,
                 file_path: str):
        self.filename = filename
        self.upload_id = upload_id
        self.file_path = file_path

class VitonImageService:
    def __init__(self, session:SessionDep, message_service: Annotated[MessageService, Depends(get_message_service)], storage_manager: Annotated[StorageManager, Depends(get_storage_manager)]):
        self.session = session
        self.message_service = message_service
        self.storage_manager = storage_manager

    def get_viton_image(self, id: uuid.UUID) -> VitonUploadImage:
        viton_image_statement = select(VitonUploadImage).where(VitonUploadImage.id == id)
        viton_image: VitonUploadImage = self.session.exec(viton_image_statement).one_or_none()
        if viton_image is None:
            raise Exception("Viton Image not found")
        return viton_image

    def create_viton_image(self, model_upload_id: uuid.UUID, cloth_upload_id: uuid.UUID, correlation_id:uuid.UUID, category:str = "upper_body") -> VitonUploadImage:
        viton_image_id = uuid.uuid4()
        viton_image = VitonUploadImage(id=viton_image_id,model_upload_id=model_upload_id, cloth_upload_id=cloth_upload_id, catergory=category, is_completed=False)
        file_upload_message = {"viton_image_id": str(viton_image_id)}
        outbound_message = OutboundMessage(content=json.dumps(file_upload_message), message_type=MessageTypes.VITON_SUBMIT_MESSAGE, correlation_id=correlation_id)
        self.message_service.create_message(outbound_message)
        self.session.add(viton_image)
        self.session.commit()
        return viton_image_id
    
    def update_viton_image(self, id: uuid.UUID, path: str, is_completed: bool) -> VitonUploadImage:
        viton_image = self.get_viton_image(id)
        viton_image.path = path
        viton_image.is_completed = is_completed
        self.session.commit()
        return viton_image
    
    def get_all_viton_images(self, is_completed=False) -> list[VitonUploadImageDto]:
        viton_image_statement = select(VitonUploadImage)
        viton_images: list[VitonUploadImage] = self.session.exec(viton_image_statement).all()
        return [VitonUploadImageDto(viton_image.catergory, viton_image.id, viton_image.path) for viton_image in viton_images]
    
    def get_image_bytes(self, id: uuid.UUID) -> bytes:
        viton_image = self.get_viton_image(id)
        return self.storage_manager.get_file(viton_image.path)