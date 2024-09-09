from abc import ABC, abstractmethod
import inspect
import sys
from app.core.deps import get_session
from app.pipeline.model.model_pipeline import ModelPipeline
from app.storage.storage_manager import StorageManager
from app.handlers.message_types import MessageTypes

# find a better injection method

class MessageHandler(ABC):
    def __init__(self,handler_name:str):
        self.handler_name = handler_name

    @abstractmethod
    async def handle(self, content:dict):
        pass
    
class UploadedImageMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.UPLOAD_MESSAGE)
        self.__model_pipeline = ModelPipeline()
        
        
    async def handle(self, content:dict):
        pipeline_parameter = {"file_id": content["file_id"], "type": content["type"]}
        pipeline_id = self.__model_pipeline.create_new_state()
        await self.__model_pipeline.process_message(pipeline_id, pipeline_parameter)
    
def MessageHandlerFactory(handler_name: str):
    current_module = sys.modules[__name__]
    for name, obj in inspect.getmembers(current_module, inspect.isclass):
        if issubclass(obj, MessageHandler) and obj is not MessageHandler:
            if obj().handler_name == handler_name:
                return obj()
    
    raise ValueError(f"No handler found for handler_name: {handler_name}")