import os
import uuid
import io
from sqlmodel import select
from app.models import FileUpload, FileUploadMetadata,FileUploadPreProcess
from app.handlers.message_types import MessageTypes
from app.storage.deps import get_storage_manager
from app.storage.storage_manager import StorageManager
from app.service.upload_image_service import get_upload_image_service
from app.pipeline import Pipeline
import logging
from app.inference import get_cloth_segmentation_inference_runtime
from utils_stableviton import center_crop
from PIL import Image

class ClothPipeline(Pipeline):
    PREPROCESS_FILE_EXTENSION="png"
    PREPROCESSED_RESIZED = "resized"
    PREPROCESSED_AGNOSTIC = "agnostic"
    IMG_H = 1024 #defalt height
    IMG_W = 768 #default width
    def __init__(self):
        super().__init__()
        self.__storage_manager: StorageManager = get_storage_manager()
        self.__logger = logging.getLogger(__name__)
        self.__upload_image_service = get_upload_image_service(self.session, self.__storage_manager, None) #message service is not needed.. need to refactor this
        
    def process_graph(self):
        return {
            0: self.process_inital_image,
            1: self.process_mask,
            2: self.complete_state
        }
    
        
    def get_file_upload(self, image_id: str) -> FileUpload:
        return self.__upload_image_service.get_uploaded_image(uuid.UUID(image_id))
    
    def get_file_upload_metadata(self, file_upload_id: uuid.UUID) -> FileUploadMetadata:
        file_upload_metadata_statement = select(FileUploadMetadata).where(FileUploadMetadata.file_upload_id == file_upload_id)
        file_upload_metadata: FileUploadMetadata = self.session.exec(file_upload_metadata_statement).one_or_none()
        if file_upload_metadata is None:
            raise Exception("File metadata not found")
        return file_upload_metadata
    
    def get_preprocessed_image(self, image_id: str, type: str) -> FileUploadPreProcess:
        return self.__upload_image_service.get_preprocessed_image(uuid.UUID(image_id), type)
        
    def get_file_upload(self, image_id: str) -> FileUpload:
        file_upload_statement = select(FileUpload).where(FileUpload.id == uuid.UUID(image_id))
        file_upload: FileUpload = self.session.exec(file_upload_statement).one_or_none()
        if file_upload is None:
            raise Exception("File not found")
        return file_upload
        
    def __resize_image(self, image: Image) -> Image:
        return image.resize((self.IMG_W, self.IMG_H))
    
    def __get_bytes_from_image(self, image: Image) -> bytes:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
        
    async def process_inital_image(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        file_upload: FileUpload = self.get_file_upload(image_id)
        file_path: str = self.__storage_manager.get_file_path(file_upload.fullpath)
        with Image.open(file_path) as image:
            width, height = image.size
            resized_image = self.__resize_image(image)
            resized_image = center_crop(resized_image)
        file_size = os.path.getsize(file_path)
        file_upload_metadata:FileUploadMetadata  = FileUploadMetadata(file_upload_id=file_upload.id, width=width, height=height, size=file_size)
        self.__logger.info(f"Processing image: {image_id}")
        self.session.add(file_upload_metadata)
        self.__upload_image_service.create_image_preprocess(file_upload.id, f"{image_id}_resized", self.__get_bytes_from_image(resized_image), self.PREPROCESS_FILE_EXTENSION, self.PREPROCESSED_RESIZED)
        self.session.commit()
        return 1
    
    async def process_mask(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        file_upload: FileUpload = self.get_file_upload(image_id)
        file_path: str = self.__storage_manager.get_file_path(file_upload.fullpath)
        agnostic_mask_bytes: bytes = get_cloth_segmentation_inference_runtime().infer(file_path)
        self.__upload_image_service.create_image_preprocess(file_upload.id, f"{image_id}_agnostic", agnostic_mask_bytes, self.PREPROCESS_FILE_EXTENSION, self.PREPROCESSED_AGNOSTIC)
        logging.getLogger(__name__).info(f"Processing image: {image_id}")
        return 2
    
    
    def get_process_message_type(self) -> str:
        return MessageTypes.CLOTH_PIPELINE_MESSAGE
    
    def get_complete_message_type(self) -> str:
        return MessageTypes.CLOTH_COMPLETE_MESSAGE
    
    def get_failure_message_type(self) -> str:
        return MessageTypes.CLOTH_ERROR_MESSAGE