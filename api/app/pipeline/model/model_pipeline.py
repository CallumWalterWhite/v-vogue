from app.pipeline import Pipeline
import logging

class ModelPipeline(Pipeline):
    def __init__(self):
        super().__init__()
        
    def process_graph(self):
        return {
            0: self.process_inital_image,
            1: self.process_agnostic_mask,
            2: self.process_openpose,
            3: self.process_denpose,
            4: self.complete_state
        }
        
    def process_inital_image(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        self.__storage_manager.get_file(f"{image_id}.jpg")
        logging.getLogger(__name__).info(f"Processing image: {image_id}")
        return 1
    
    def process_agnostic_mask(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        self.__storage_manager.get_file(f"{image_id}.jpg")
        logging.getLogger(__name__).info(f"Processing image: {image_id}")
        return 2
    
    def process_openpose(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        self.__storage_manager.get_file(f"{image_id}.jpg")
        logging.getLogger(__name__).info(f"Processing image: {image_id}")
        return 3
    
    def process_denpose(self, parameter: dict) -> int:
        image_id: str = parameter["file_id"]
        self.__storage_manager.get_file(f"{image_id}.jpg")
        logging.getLogger(__name__).info(f"Processing image: {image_id}")
        return 4