from abc import ABC, abstractmethod
import inspect
import sys
import uuid
from app.pipeline import Pipeline
from app.pipeline.model.model_pipeline import ModelPipeline
from app.pipeline.cloth.cloth_pipeline import ClothPipeline
from app.pipeline.viton.viton_pipeline import VitonHDPipeline
from app.handlers.message_types import MessageTypes
from app.core.deps import get_session
from app.models import FileUploadPipeline


class PipelineFactory():
    @staticmethod
    def create_pipeline(pipeline_type: str) -> Pipeline:
        if pipeline_type == "model":
            return ModelPipeline()
        if pipeline_type == "cloth":
            return ClothPipeline()
        raise ValueError("Pipeline type not found")
    
    @staticmethod
    def create_viton_pipeline() -> Pipeline:
        return VitonHDPipeline()

#TODO: find a better injection method

class MessageHandler(ABC):
    def __init__(self,handler_name:str):
        self.handler_name = handler_name

    @abstractmethod
    async def handle(self, content:dict, correlation_id:uuid.UUID):
        pass
    
class UploadedImageMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.UPLOAD_MESSAGE)
        self.__session = get_session()
        
        
    async def handle(self, content:dict, correlation_id:uuid.UUID):
        pipeline = PipelineFactory.create_pipeline(content["type"])
        pipeline_parameter = {"file_id": content["file_id"], "type": content["type"], "correlation_id": str(correlation_id)}
        pipeline_id: str = pipeline.create_new_state(pipeline_parameter)
        self.__session.add(FileUploadPipeline(pipeline_id=uuid.UUID(pipeline_id), file_upload_id=uuid.UUID(content["file_id"])))
        self.__session.commit()
        await pipeline.process_message(pipeline_id, pipeline_parameter)

class ModelPipelineProcessMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.MODEL_PIPELINE_MESSAGE)
        self.__model_pipeline = ModelPipeline()
        
    async def handle(self, content:dict, correlation_id:uuid.UUID):
        pipeline_id = content["pipeline_id"]
        pipeline_parameter = {"file_id": content["parameters"]["file_id"], "type": content["parameters"]["type"], "correlation_id": str(correlation_id)}
        await self.__model_pipeline.process_message(pipeline_id, pipeline_parameter)
    
class ModelPipelineCompleteMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.MODEL_COMPLETE_MESSAGE)
        
    async def handle(self, content:dict, correlation_id:uuid.UUID):
        pass
    
class ModelPipelineErrorMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.MODEL_ERROR_MESSAGE)
        
    async def handle(self, content:dict, correlation_id:uuid.UUID):
        pass

class ClothPipelineProcessMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.CLOTH_PIPELINE_MESSAGE)
        self.__cloth_pipeline = ClothPipeline()
        
    async def handle(self, content:dict, correlation_id:uuid.UUID):
        pipeline_id = content["pipeline_id"]
        pipeline_parameter = {"file_id": content["parameters"]["file_id"], "type": content["parameters"]["type"], "correlation_id": str(correlation_id)}
        await self.__cloth_pipeline.process_message(pipeline_id, pipeline_parameter)
    
class ClothPipelineCompleteMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.CLOTH_COMPLETE_MESSAGE)
        
    async def handle(self, content:dict, correlation_id:uuid.UUID):
        pass
    
class ClothPipelineErrorMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.CLOTH_ERROR_MESSAGE)
        
    async def handle(self, content:dict, correlation_id:uuid.UUID):
        pass
    

class VitonSubmitMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.VITON_SUBMIT_MESSAGE)
        self.__session = get_session()
        
        
    async def handle(self, content:dict, correlation_id:uuid.UUID):
        pipeline = PipelineFactory.create_viton_pipeline()
        pipeline_parameter = {"viton_image_id": content["viton_image_id"], "correlation_id": str(correlation_id)}
        pipeline_id: str = pipeline.create_new_state(pipeline_parameter)
        self.__session.add(FileUploadPipeline(pipeline_id=uuid.UUID(pipeline_id), file_upload_id=uuid.UUID(content["viton_image_id"])))
        self.__session.commit()
        await pipeline.process_message(pipeline_id, pipeline_parameter)

class VitonPipelineProcessMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.VITON_PIPELINE_MESSAGE)
        self.__viton_pipeline = PipelineFactory.create_viton_pipeline()
        
    async def handle(self, content:dict, correlation_id:uuid.UUID):
        pipeline_id = content["pipeline_id"]
        pipeline_parameter = {"viton_image_id": content["parameters"]["viton_image_id"], "correlation_id": str(correlation_id)}
        await self.__viton_pipeline.process_message(pipeline_id, pipeline_parameter)
    
class VitonPipelineCompleteMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.VITON_COMPLETE_MESSAGE)
        
    async def handle(self, content:dict, correlation_id:uuid.UUID):
        pass
    
class VitonPipelineErrorMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.VITON_ERROR_MESSAGE)
        
    async def handle(self, content:dict, correlation_id:uuid.UUID):
        pass
    

def MessageHandlerFactory(handler_name: str):
    current_module = sys.modules[__name__]
    for name, obj in inspect.getmembers(current_module, inspect.isclass):
        if issubclass(obj, MessageHandler) and obj is not MessageHandler:
            if obj().handler_name == handler_name:
                return obj()
    
    raise ValueError(f"No handler found for handler_name: {handler_name}")