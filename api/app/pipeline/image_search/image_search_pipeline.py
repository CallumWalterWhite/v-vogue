from bs4 import BeautifulSoup
from fastapi import HTTPException
import requests
from app.handlers.message_types import MessageTypes
from app.pipeline import Pipeline
from app.pipeline.image_search.search_similar_images_selenium import search_similar_images_selenium

class ImageSearchPipeline(Pipeline):
    
    def __init__(self):
        super().__init__("image_search")
        
    def process_graph(self):
        return {
            0: self.upload_image,
            1: self.similarity_search,
            2: self.remove_image,
            3: self.complete_state
        }
    
    async def upload_image(self, parameter: dict) -> int:
        #TODO: upload image to public storage
        return 1
    
    async def similarity_search(self, parameter: dict) -> int:
        image_url: str
        if not image_url.startswith("http"):
            raise HTTPException(status_code=400, detail="Invalid image URL")
        try:
            similar_images = search_similar_images_selenium(image_url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        return 2
        
    async def remove_image(self, parameter: dict) -> int:
        #TODO: remove image from public storage
        return 3
    
    def get_process_message_type(self) -> str:
        return MessageTypes.CLOTH_PIPELINE_MESSAGE
    
    def get_complete_message_type(self) -> str:
        return MessageTypes.CLOTH_COMPLETE_MESSAGE
    
    def get_failure_message_type(self) -> str:
        return MessageTypes.CLOTH_ERROR_MESSAGE