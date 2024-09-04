from abc import ABC, abstractmethod
import inspect
import sys
from app.handlers.message_types import MessageTypes

class MessageHandler(ABC):
    def __init__(self,handler_name:str):
        self.handler_name = handler_name

    @abstractmethod
    async def handle(self, content:dict):
        pass
    
class UploadedImageMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__(MessageTypes.UPLOAD_MESSAGE)
        
    async def handle(self, content:dict):
        print(f"Handling uploaded image: {content}")
    
def MessageHandlerFactory(handler_name: str):
    current_module = sys.modules[__name__]
    for name, obj in inspect.getmembers(current_module, inspect.isclass):
        if issubclass(obj, MessageHandler) and obj is not MessageHandler:
            if obj().handler_name == handler_name:
                return obj()
    
    raise ValueError(f"No handler found for handler_name: {handler_name}")