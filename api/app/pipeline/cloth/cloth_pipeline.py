import uuid
from sqlmodel import select
from app.models import FileUpload
from app.handlers.message_types import MessageTypes
from app.storage.deps import get_storage_manager
from app.storage.storage_manager import StorageManager
from app.pipeline import Pipeline
import logging
from app.inference import get_cloth_segmentation_inference_runtime

class ModelPipeline(Pipeline):
    AGNOSTIC_FILE_EXTENSION="png"
    def __init__(self):
        self.__message_type = MessageTypes.MODEL_PIPELINE_MESSAGE
        self.__storage_manager: StorageManager = get_storage_manager()
        super().__init__()
        
    def process_graph(self):
        return {
            0: self.process_inital_image,
            1: self.process_mask,
            2: self.complete_state
        }
        
    def get_file_upload(self, image_id: str) -> FileUpload:
        file_upload_statement = select(FileUpload).where(FileUpload.id == uuid.UUID(image_id))
        file_upload: FileUpload = self.session.exec(file_upload_statement).one_or_none()
        if file_upload is None:
            raise Exception("File not found")
        return file_upload
        
        
    def process_inital_image(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        self.__storage_manager.get_file(f"{image_id}.jpg")
        logging.getLogger(__name__).info(f"Processing image: {image_id}")
        return 1
    
    def process_mask(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        file_upload: FileUpload = self.get_file_upload(image_id)
        file_path: str = self.__storage_manager.get_file_path(file_upload.fullpath)
        agnostic_mask_bytes: bytes = get_cloth_segmentation_inference_runtime().infer(file_path)
        agnostic_file_path = f"{image_id}_agnostic.{self.AGNOSTIC_FILE_EXTENSION}"
        self.__storage_manager.create_file(agnostic_file_path, agnostic_mask_bytes)
        logging.getLogger(__name__).info(f"Processing image: {image_id}")
        return 2
    
    def get_process_message_type(self) -> str:
        return self.__message_type
    
    def get_complete_message_type(self) -> str:
        return ""
    
    def get_failure_message_type(self) -> str:
        return ""