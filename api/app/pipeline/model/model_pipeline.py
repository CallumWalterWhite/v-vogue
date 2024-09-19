import uuid
import os
from sqlmodel import select
from app.storage.storage_manager import StorageManager
from app.storage.deps import get_storage_manager
from app.models import FileUpload, FileUploadMetadata, ModelImageMetadata,FileUploadPreProcess
from app.pipeline import Pipeline
import logging
from app.handlers.message_types import MessageTypes
from app.service.upload_image_service import get_upload_image_service
from app.inference import get_cloth_segmentation_inference_runtime, get_openpose_runtime, get_humanparsing_runtime, get_densepose_runtime
from utils_stableviton import get_mask_location, center_crop
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
    PREPROCESS_FILE_EXTENSION = "png"
    PREPROCESSED_RESIZED = "resized"
    PREPROCESSED_AGNOSTIC = "agnostic"
    PREPROCESSED_AGNOSTIC_V2 = "agnostic_v2"
    PREPROCESSED_DENSEPOSE = "densepose"
    IMG_H = 512 #defalt height
    IMG_W = 384 #default width
    def __init__(self):
        super().__init__()
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
    
    async def process_openpose(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        file_preprocess: FileUploadPreProcess = self.get_preprocessed_image(image_id, self.PREPROCESSED_RESIZED)
        file_path: str = self.__storage_manager.get_file_path(file_preprocess.fullpath)
        openpose_runtime = get_openpose_runtime()
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

        # agnostic_mask_bytes: bytes = get_cloth_segmentation_inference_runtime().infer(file_path)
        # self.__upload_image_service.create_image_preprocess(file_upload.id, f"{image_id}_agnostic", agnostic_mask_bytes, self.PREPROCESS_FILE_EXTENSION, self.PREPROCESSED_AGNOSTIC)

        model_parse = get_humanparsing_runtime().infer(file_path)
        image_parse = model_parse[0]
        model_metadata: ModelImageMetadata = self.get_model_image_metadata(file_upload.id)
        pose_data = json.loads(model_metadata.keypoints)
        mask, mask_gray = get_mask_location('hd', self.category_dict_utils[0], image_parse, pose_data, radius=5)
        mask = mask.resize((self.IMG_W, self.IMG_H), Image.NEAREST)
        mask_gray = mask_gray.resize((self.IMG_W, self.IMG_H), Image.NEAREST)
        masked_vton_img = Image.composite(mask_gray, vton_img, mask)

        self.__upload_image_service.create_image_preprocess(file_upload.id, f"{image_id}_v2_agnostic", self.__get_bytes_from_image(masked_vton_img), self.PREPROCESS_FILE_EXTENSION, self.PREPROCESSED_AGNOSTIC_V2)


        self.__logger.info(f"Processing image: {image_id}")
        return 3
    
    async def process_densepose(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        file_upload: FileUpload = self.get_file_upload(image_id)
        file_preprocess: FileUploadPreProcess = self.get_preprocessed_image(image_id, self.PREPROCESSED_RESIZED)
        file_path: str = self.__storage_manager.get_file_path(file_preprocess.fullpath)

        model_denpose = get_densepose_runtime()
        denpose: Image = model_denpose.infer(file_path)
        
        self.__upload_image_service.create_image_preprocess(file_upload.id, f"{image_id}_densepose", self.__get_bytes_from_image(denpose), self.PREPROCESS_FILE_EXTENSION, self.PREPROCESSED_DENSEPOSE)

        self.__logger.info(f"Processing image: {image_id}")
        return 4
    
    def get_process_message_type(self) -> str:
        return MessageTypes.MODEL_PIPELINE_MESSAGE
    
    def get_complete_message_type(self) -> str:
        return MessageTypes.MODEL_COMPLETE_MESSAGE
    
    def get_failure_message_type(self) -> str:
        return MessageTypes.MODEL_ERROR_MESSAGE