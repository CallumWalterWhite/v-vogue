import uuid
import os
from sqlmodel import select
from app.storage.storage_manager import StorageManager
from app.storage.deps import get_storage_manager
from app.models import FileUpload, FileUploadMetadata, ModelImageMetadata
from app.pipeline import Pipeline
import logging
from app.handlers.message_types import MessageTypes
from app.inference import get_cloth_segmentation_inference_runtime, get_openpose_runtime, get_humanparsing_runtime, get_densepose_runtime
from utils_stableviton import get_mask_location, get_batch, tensor2img, center_crop
from app.inference.openpose_inference import OpenPoseKeypoins
from enum import Enum
from PIL import Image
import json
import io

class ModelPipelineProcess(Enum):
    INITIAL_IMAGE = 0
    AGNOSTIC_MASK = 1
    OPENPOSE = 2
    DENPOSE = 3
    COMPLETE = 4

class ModelPipeline(Pipeline):
    #TODO: parse all 3 categories to get the mask and create matrix for the mask with the garment, DEFAULT is upper_body
    category_dict_utils = ['upper_body', 'lower_body', 'dresses']
    AGNOSTIC_FILE_EXTENSION = "png"
    IMG_H = 1024 #defalt height
    IMG_W = 768 #default width
    def __init__(self):
        self.__storage_manager: StorageManager = get_storage_manager()
        self.__logger = logging.getLogger(__name__)
        super().__init__()
        
    def process_graph(self):
        return {
            0: self.process_inital_image,
            1: self.process_openpose,
            2: self.process_agnostic_mask,
            3: self.process_denpose,
            4: self.complete_state
        }
        
    def get_file_upload(self, image_id: str) -> FileUpload:
        file_upload_statement = select(FileUpload).where(FileUpload.id == uuid.UUID(image_id))
        file_upload: FileUpload = self.session.exec(file_upload_statement).one_or_none()
        if file_upload is None:
            raise Exception("File not found")
        return file_upload
    
    def get_file_upload_metadata(self, file_upload_id: uuid.UUID) -> FileUploadMetadata:
        file_upload_metadata_statement = select(FileUploadMetadata).where(FileUploadMetadata.file_upload_id == file_upload_id)
        file_upload_metadata: FileUploadMetadata = self.session.exec(file_upload_metadata_statement).one_or_none()
        if file_upload_metadata is None:
            raise Exception("File metadata not found")
        return file_upload_metadata
    
    def get_model_image_metadata(self, file_upload_id: uuid.UUID) -> ModelImageMetadata:
        model_image_metadata_statement = select(ModelImageMetadata).where(ModelImageMetadata.file_upload_id == file_upload_id)
        model_image_metadata: ModelImageMetadata = self.session.exec(model_image_metadata_statement).one_or_none()
        if model_image_metadata is None:
            raise Exception("Model metadata not found")
        return model_image_metadata
        
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
        return 2
    
    async def process_agnostic_mask(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        file_upload: FileUpload = self.get_file_upload(image_id)
        file_path: str = self.__storage_manager.get_file_path(file_upload.fullpath)
        vton_img = Image.open(file_path)
        agnostic_mask_bytes: bytes = get_cloth_segmentation_inference_runtime().infer(file_path)
        agnostic_file_path = f"{image_id}_agnostic.{self.AGNOSTIC_FILE_EXTENSION}"
        self.__storage_manager.create_file(agnostic_file_path, agnostic_mask_bytes)
        model_parse = get_humanparsing_runtime().infer(file_path)
        image_parse = model_parse[0]
        model_metadata: ModelImageMetadata = self.get_model_image_metadata(file_upload.id)
        pose_data = json.loads(model_metadata.keypoints)
        mask, mask_gray = get_mask_location('hd', self.category_dict_utils[0], image_parse, pose_data, radius=5)
        mask = mask.resize((self.IMG_W, self.IMG_H), Image.NEAREST)
        mask_gray = mask_gray.resize((self.IMG_W, self.IMG_H), Image.NEAREST)
        masked_vton_img = Image.composite(mask_gray, vton_img, mask)
        agnostic_file_v2_path = f"{image_id}_v2_agnostic.{self.AGNOSTIC_FILE_EXTENSION}"
        img_byte_arr = io.BytesIO()
        masked_vton_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        self.__storage_manager.create_file(agnostic_file_v2_path, img_byte_arr)
        self.__logger.info(f"Processing image: {image_id}")
        return 3
    
    async def process_denpose(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        file_upload: FileUpload = self.get_file_upload(image_id)
        file_path: str = self.__storage_manager.get_file_path(file_upload.fullpath)
        model_denpose = get_densepose_runtime()
        denpose = model_denpose.infer(file_path)
        print(denpose)
        raise Exception(type(denpose))
        return 4
    
    def get_process_message_type(self) -> str:
        return MessageTypes.MODEL_PIPELINE_MESSAGE
    
    def get_complete_message_type(self) -> str:
        return MessageTypes.MODEL_COMPLETE_MESSAGE
    
    def get_failure_message_type(self) -> str:
        return MessageTypes.MODEL_ERROR_MESSAGE