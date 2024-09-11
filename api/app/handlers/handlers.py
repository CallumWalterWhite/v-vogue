from abc import ABC, abstractmethod
import inspect
import sys
import uuid
from app.pipeline.model.model_pipeline import ModelPipeline
from app.handlers.message_types import MessageTypes
from app.core.deps import get_session
from app.models import FileUploadPipeline

# find a better injection method

class MessageHandler(ABC):
    def __init__(self,handler_name:str):
        self.handler_name = handler_name

    @abstractmethod
    async def handle(self, content:dict, correlation_id:str):
        pass
    
class UploadedImageMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.UPLOAD_MESSAGE)
        self.__model_pipeline = ModelPipeline()
        self.__session = get_session()
        
        
    async def handle(self, content:dict, correlation_id:str):
        pipeline_parameter = {"file_id": content["file_id"], "type": content["type"], "correlation_id": correlation_id}
        pipeline_id: str = self.__model_pipeline.create_new_state(pipeline_parameter)
        self.__session.add(FileUploadPipeline(pipeline_id=uuid.UUID(pipeline_id), file_id=uuid.UUID(content["file_id"])))
        self.__session.commit()
        await self.__model_pipeline.process_message(pipeline_id, pipeline_parameter)

class ModelPipelineProcessMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.MODEL_PIPELINE_MESSAGE)
        self.__model_pipeline = ModelPipeline()
        
    async def handle(self, content:dict, correlation_id:str):
        pipeline_id = content["pipeline_id"]
        pipeline_parameter = {"file_id": content["parameters"]["file_id"], "type": content["parameters"]["type"], "correlation_id": correlation_id}
        await self.__model_pipeline.process_message(pipeline_id, pipeline_parameter)
    
class ModelPipelineCompleteMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.MODEL_COMPLETE_MESSAGE)
        
    async def handle(self, content:dict, correlation_id:str):
        pass
    
class ModelPipelineErrorMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.MODEL_ERROR_MESSAGE)
        
    async def handle(self, content:dict, correlation_id:str):
        pass
    
def MessageHandlerFactory(handler_name: str):
    current_module = sys.modules[__name__]
    for name, obj in inspect.getmembers(current_module, inspect.isclass):
        if issubclass(obj, MessageHandler) and obj is not MessageHandler:
            if obj().handler_name == handler_name:
                return obj()
    
    raise ValueError(f"No handler found for handler_name: {handler_name}")