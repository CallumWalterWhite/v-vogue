from app.handlers.message_types import MessageTypes
from app.storage.deps import get_storage_manager
from app.storage.storage_manager import StorageManager
from app.pipeline import Pipeline
import logging

class ModelPipeline(Pipeline):
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
        
    def process_inital_image(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        self.__storage_manager.get_file(f"{image_id}.jpg")
        logging.getLogger(__name__).info(f"Processing image: {image_id}")
        return 1
    
    def process_mask(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        self.__storage_manager.get_file(f"{image_id}.jpg")
        logging.getLogger(__name__).info(f"Processing image: {image_id}")
        return 2
    
    def get_process_message_type(self) -> str:
        return self.__message_type
    
    def get_complete_message_type(self) -> str:
        return ""
    
    def get_failure_message_type(self) -> str:
        return ""