import uuid
import os
from sqlmodel import select
from app.inference.base_inference import BaseInference
from app.storage.storage_manager import StorageManager
from app.storage.deps import get_storage_manager
from app.models import FileUpload, FileUploadMetadata, ModelImageMetadata,FileUploadPreProcess
from app.pipeline import Pipeline
import logging
from app.handlers.message_types import MessageTypes
from app.service.upload_image_service import get_upload_image_service
from app.inference import InferenceManager
from utils_stableviton import get_mask_location, center_crop
from app.inference.openpose_inference import OpenPoseKeypoins
from app.pipeline.util import convert_pil_image_to_bytes
from enum import Enum
from PIL import Image
import json

class ModelPipelineProcess(int, Enum):
    INITIAL_IMAGE = 0
    AGNOSTIC_MASK = 1
    OPENPOSE = 2
    DENPOSE = 3
    COMPLETE = 4

class ModelPipeline(Pipeline):
    #TODO: parse all 3 categories to get the mask and create matrix for the mask with the garment, DEFAULT is upper_body
    CATEGORY_DICT_UTILS = ['upper_body', 'lower_body', 'dresses']
    DEFAULT_CATEGORY = 0
    PREPROCESS_FILE_EXTENSION = "png"
    PREPROCESSED_RESIZED = "resized"
    PREPROCESSED_AGNOSTIC = "agnostic"
    PREPROCESSED_AGNOSTIC_V2 = "agnostic_v2"
    PREPROCESSED_DENSEPOSE = "densepose"
    IMG_H = BaseInference.IMG_H
    IMG_W = BaseInference.IMG_W
    def __init__(self):
        super().__init__("model")
        self.__storage_manager: StorageManager = get_storage_manager()
        self.__logger = logging.getLogger(__name__)
        self.__upload_image_service = get_upload_image_service(self.session, self.__storage_manager, None) #message service is not needed.. need to refactor this
        
    def process_graph(self):
        return {
            0: self.process_inital_image,
            1: self.process_openpose,
            2: self.process_agnostic_mask,
            3: self.process_densepose,
            4: self.complete_state
        }
        
    def get_file_upload(self, image_id: str) -> FileUpload:
        return self.__upload_image_service.get_uploaded_image(uuid.UUID(image_id))
    
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
    
    def get_preprocessed_image(self, image_id: str, type: str) -> FileUploadPreProcess:
        return self.__upload_image_service.get_preprocessed_image(uuid.UUID(image_id), type)

    def __resize_image(self, image: Image) -> Image:
        return image.resize((self.IMG_W, self.IMG_H))
        
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
        self.__upload_image_service.create_image_preprocess(file_upload.id, f"{image_id}_resized", convert_pil_image_to_bytes(resized_image), self.PREPROCESS_FILE_EXTENSION, self.PREPROCESSED_RESIZED)
        self.session.commit()
        return 1
    
    async def process_openpose(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        file_preprocess: FileUploadPreProcess = self.get_preprocessed_image(image_id, self.PREPROCESSED_RESIZED)
        file_path: str = self.__storage_manager.get_file_path(file_preprocess.fullpath)
        openpose_runtime = InferenceManager.get_openpose_runtime()
        keypoints: OpenPoseKeypoins = openpose_runtime.infer(file_path)
        model_keypoints: ModelImageMetadata = ModelImageMetadata(file_upload_id=file_preprocess.orginal_file_upload_id, keypoints=json.dumps(keypoints.pose_keypoints_2d))
        self.session.add(model_keypoints)
        self.session.commit()
        self.__logger.info(f"Processing image: {image_id}")
        return 2
    
    async def process_agnostic_mask(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        file_upload: FileUpload = self.get_file_upload(image_id)
        file_preprocess: FileUploadPreProcess = self.get_preprocessed_image(image_id, self.PREPROCESSED_RESIZED)
        file_path: str = self.__storage_manager.get_file_path(file_preprocess.fullpath)
        vton_img = Image.open(file_path)
        
        humanparsing_runtime = InferenceManager.get_humanparsing_runtime()
        model_parse = humanparsing_runtime.infer(file_path)
        image_parse = model_parse[0]
        model_metadata: ModelImageMetadata = self.get_model_image_metadata(file_upload.id)
        pose_data = json.loads(model_metadata.keypoints)
        
        mask, mask_gray = get_mask_location('hd', self.CATEGORY_DICT_UTILS[self.DEFAULT_CATEGORY], image_parse, pose_data, radius=5, width=self.IMG_W, height=self.IMG_H)
        mask = mask.resize((self.IMG_W, self.IMG_H), Image.NEAREST)
        mask_gray = mask_gray.resize((self.IMG_W, self.IMG_H), Image.NEAREST)
        masked_vton_img = Image.composite(mask_gray, vton_img, mask)
        mask_bytes = convert_pil_image_to_bytes(mask)
        masked_vton_img_bytes = convert_pil_image_to_bytes(masked_vton_img)
        
        model_metadata.mask = mask_bytes
        model_metadata.masked_image = masked_vton_img_bytes

        self.__upload_image_service.create_image_preprocess(file_upload.id, f"{image_id}_v2_agnostic", masked_vton_img_bytes, self.PREPROCESS_FILE_EXTENSION, self.PREPROCESSED_AGNOSTIC_V2)
        
        self.session.commit()

        self.__logger.info(f"Processing image: {image_id}")
        return 3
    
    async def process_densepose(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        file_upload: FileUpload = self.get_file_upload(image_id)
        file_preprocess: FileUploadPreProcess = self.get_preprocessed_image(image_id, self.PREPROCESSED_RESIZED)
        file_path: str = self.__storage_manager.get_file_path(file_preprocess.fullpath)
        
        model_metadata: ModelImageMetadata = self.get_model_image_metadata(file_upload.id)
        
        model_denpose = InferenceManager.get_densepose_runtime()
        denpose: Image = model_denpose.infer(file_path)
        densepose_bytes: bytes = convert_pil_image_to_bytes(denpose)
        model_metadata.densepose = densepose_bytes
        
        self.__upload_image_service.create_image_preprocess(file_upload.id, f"{image_id}_densepose", densepose_bytes, self.PREPROCESS_FILE_EXTENSION, self.PREPROCESSED_DENSEPOSE)

        self.__logger.info(f"Processing image: {image_id}")
        return 4
    
    def get_process_message_type(self) -> str:
        return MessageTypes.MODEL_PIPELINE_MESSAGE
    
    def get_complete_message_type(self) -> str:
        return MessageTypes.MODEL_COMPLETE_MESSAGE
    
    def get_failure_message_type(self) -> str:
        return MessageTypes.MODEL_ERROR_MESSAGE