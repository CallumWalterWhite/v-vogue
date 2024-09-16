import uuid
import os
from sqlmodel import select
from app.storage.storage_manager import StorageManager
from app.storage.deps import get_storage_manager
from app.models import FileUpload, FileUploadMetadata, ModelImageMetadata
from app.pipeline import Pipeline
import logging
from app.handlers.message_types import MessageTypes
from app.inference import get_cloth_segmentation_inference_runtime, get_openpose_runtime, get_humanparsing_runtime
from app.inference.openpose_inference import OpenPoseKeypoins
from enum import Enum
from PIL import Image
import json

class ModelPipelineProcess(Enum):
    INITIAL_IMAGE = 0
    AGNOSTIC_MASK = 1
    OPENPOSE = 2
    DENPOSE = 3
    COMPLETE = 4

class ModelPipeline(Pipeline):
    AGNOSTIC_FILE_EXTENSION = "png"
    def __init__(self):
        self.__storage_manager: StorageManager = get_storage_manager()
        self.__logger = logging.getLogger(__name__)
        super().__init__()
        
    def process_graph(self):
        return {
            0: self.process_inital_image,
            1: self.process_agnostic_mask,
            2: self.process_openpose,
            3: self.process_denpose,
            4: self.complete_state
        }
        
    def get_file_upload(self, image_id: str) -> FileUpload:
        file_upload_statement = select(FileUpload).where(FileUpload.id == uuid.UUID(image_id))
        file_upload: FileUpload = self.session.exec(file_upload_statement).one_or_none()
        if file_upload is None:
            raise Exception("File not found")
        return file_upload
        
    async def process_inital_image(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        file_upload: FileUpload = self.get_file_upload(image_id)
        file_path: str = self.__storage_manager.get_file_path(file_upload.fullpath)
        with Image.open(file_path) as image:
            width, height = image.size
        file_size = os.path.getsize(file_path)
        file_upload_metadata:FileUploadMetadata  = FileUploadMetadata(file_upload_id=file_upload.id, width=width, height=height, size=file_size)
        self.__logger.info(f"Processing image: {image_id}")
        self.session.add(file_upload_metadata)
        self.session.commit()
        return 1
    
    async def process_agnostic_mask(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        file_upload: FileUpload = self.get_file_upload(image_id)
        file_path: str = self.__storage_manager.get_file_path(file_upload.fullpath)
        agnostic_mask_bytes: bytes = get_cloth_segmentation_inference_runtime().infer(file_path)
        agnostic_file_path = f"{image_id}_agnostic.{self.AGNOSTIC_FILE_EXTENSION}"
        self.__storage_manager.create_file(agnostic_file_path, agnostic_mask_bytes)
        get_humanparsing_runtime().infer(file_path)
        #TODO: add agnostic mask 3.2
        self.__logger.info(f"Processing image: {image_id}")
        return 2
    
    async def process_openpose(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        file_upload: FileUpload = self.get_file_upload(image_id)
        file_path: str = self.__storage_manager.get_file_path(file_upload.fullpath)
        openpose_runtime = get_openpose_runtime()
        keypoints: OpenPoseKeypoins = openpose_runtime.infer(file_path, 512)
        model_keypoints: ModelImageMetadata = ModelImageMetadata(file_upload_id=file_upload.id, keypoints=json.dumps(keypoints.pose_keypoints_2d))
        self.session.add(model_keypoints)
        self.session.commit()
        self.__logger.info(f"Processing image: {image_id}")
        return 3
    
    async def process_denpose(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        self.__storage_manager.get_file(f"{image_id}.png")
        #TODO: run denpose https://github.com/facebookresearch/detectron2
        self.__logger.info(f"Processing image: {image_id}")
        return 4
    
    def get_process_message_type(self) -> str:
        return MessageTypes.MODEL_PIPELINE_MESSAGE
    
    def get_complete_message_type(self) -> str:
        return MessageTypes.MODEL_COMPLETE_MESSAGE
    
    def get_failure_message_type(self) -> str:
        return MessageTypes.MODEL_ERROR_MESSAGE