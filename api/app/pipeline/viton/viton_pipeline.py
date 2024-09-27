import uuid
from sqlmodel import select
from app.service.viton_service import get_viton_image_service
from app.storage.storage_manager import StorageManager
from app.storage.deps import get_storage_manager
from app.models import FileUpload, FileUploadMetadata, ModelImageMetadata,FileUploadPreProcess, VitonUploadImage
from app.pipeline import Pipeline
import logging
from app.pipeline.util import convert_bytes_to_pil_image
from app.handlers.message_types import MessageTypes
from app.service.upload_image_service import get_upload_image_service
from app.inference import InferenceManager
from app.inference.base_inference import BaseInference
from utils_stableviton import get_batch
from enum import Enum
from PIL import Image
import io

class ModelPipelineProcess(Enum):
    INITIAL_IMAGE = 0
    AGNOSTIC_MASK = 1
    OPENPOSE = 2
    DENPOSE = 3
    COMPLETE = 4

class VitonHDPipeline(Pipeline):
    #TODO: parse all 3 categories to get the mask and create matrix for the mask with the garment, DEFAULT is upper_body
    category_dict_utils = ['upper_body', 'lower_body', 'dresses']
    PREPROCESS_FILE_EXTENSION = "png"
    OUTPUT_FILE_EXTENSION="png"
    PREPROCESSED_RESIZED = "resized"
    IMG_H = BaseInference.IMG_H
    IMG_W = BaseInference.IMG_W
    def __init__(self):
        super().__init__("viton")
        self.__storage_manager: StorageManager = get_storage_manager()
        self.__logger = logging.getLogger(__name__)
        self.__upload_image_service = get_upload_image_service(self.session, self.__storage_manager, None) #message service is not needed.. need to refactor this
        self.__viton_image_service = get_viton_image_service(self.session, None)

    def process_graph(self):
        return {
            0: self.process_inital_image,
            1: self.complete_state
        }
        
    def get_file_upload(self, image_id: uuid.UUID) -> FileUpload:
        return self.__upload_image_service.get_uploaded_image(image_id)
    
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
    
    def get_viton_image(self, id: str) -> VitonUploadImage:
        return self.__viton_image_service.get_viton_image(uuid.UUID(id))
    
    def get_preprocessed_image(self, image_id: uuid.UUID, type: str) -> FileUploadPreProcess:
        return self.__upload_image_service.get_preprocessed_image(image_id, type)
    
    def __get_bytes_from_image(self, image: Image) -> bytes:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
        
    async def process_inital_image(self, parameter: dict) -> int:
        id: str = parameter["viton_image_id"]
        viton_image: VitonUploadImage = self.get_viton_image(id)
        model_file_upload_id: FileUpload = self.get_file_upload(viton_image.model_upload_id)
        cloth_file_upload_id: FileUpload = self.get_file_upload(viton_image.cloth_upload_id)

        model_image_metadata: ModelImageMetadata = self.get_model_image_metadata(viton_image.model_upload_id)
        
        resized_model_image = self.get_preprocessed_image(model_file_upload_id.id, self.PREPROCESSED_RESIZED)
        resized_cloth_image = self.get_preprocessed_image(cloth_file_upload_id.id, self.PREPROCESSED_RESIZED)

        resized_file_path: str = self.__storage_manager.get_file_path(resized_model_image.fullpath)
        cloth_file_path: str = self.__storage_manager.get_file_path(resized_cloth_image.fullpath)

        vton_img: Image = Image.open(resized_file_path).convert('RGB')
        garm_img: Image = Image.open(cloth_file_path).convert('RGB')
        
        mask: Image = convert_bytes_to_pil_image(model_image_metadata.mask)
        masked_vton_img: Image = convert_bytes_to_pil_image(model_image_metadata.masked_image)
        densepose: Image = convert_bytes_to_pil_image(model_image_metadata.densepose)
        
        batch = get_batch(
            vton_img, 
            garm_img, 
            densepose, 
            masked_vton_img, 
            mask, 
            self.IMG_H, 
            self.IMG_W
        )

        vitonHD_runtime = InferenceManager.get_vitonHD_runtime()

        result = vitonHD_runtime.infer(batch, 20)
        results_bytes = self.__get_bytes_from_image(result)
        self.__storage_manager.create_file(f'{id}.{self.OUTPUT_FILE_EXTENSION}', results_bytes)
        self.__viton_image_service.update_viton_image(uuid.UUID(id), f'{id}.{self.OUTPUT_FILE_EXTENSION}', True)
        return 1
    
    def get_process_message_type(self) -> str:
        return MessageTypes.MODEL_PIPELINE_MESSAGE
    
    def get_complete_message_type(self) -> str:
        return MessageTypes.MODEL_COMPLETE_MESSAGE
    
    def get_failure_message_type(self) -> str:
        return MessageTypes.MODEL_ERROR_MESSAGE