from app.storage.storage_manager import StorageManager
from app.storage.deps import get_storage_manager
from app.pipeline import Pipeline
import logging
from app.handlers.message_types import MessageTypes

class ModelPipeline(Pipeline):
    def __init__(self):
        self.__storage_manager: StorageManager = get_storage_manager()
        super().__init__()
        
    def process_graph(self):
        return {
            0: self.process_inital_image,
            1: self.process_agnostic_mask,
            2: self.process_openpose,
            3: self.process_denpose,
            4: self.complete_state
        }
        
    async def process_inital_image(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        file:bytes = self.__storage_manager.get_file(f"{image_id}.png")
        logging.getLogger(__name__).info(f"Processing image: {image_id}")
        return 1
    
    async def process_agnostic_mask(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        self.__storage_manager.get_file(f"{image_id}.png")
        logging.getLogger(__name__).info(f"Processing image: {image_id}")
        return 2
    
    async def process_openpose(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        self.__storage_manager.get_file(f"{image_id}.png")
        logging.getLogger(__name__).info(f"Processing image: {image_id}")
        return 3
    
    async def process_denpose(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        self.__storage_manager.get_file(f"{image_id}.png")
        logging.getLogger(__name__).info(f"Processing image: {image_id}")
        return 4
    
    def get_process_message_type(self) -> str:
        return MessageTypes.MODEL_PIPELINE_MESSAGE
    
    def get_complete_message_type(self) -> str:
        return MessageTypes.MODEL_COMPLETE_MESSAGE
    
    def get_failure_message_type(self) -> str:
        return MessageTypes.MODEL_ERROR_MESSAGE