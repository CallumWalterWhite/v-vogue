import json
from app.core.config import settings
import httpx
from pydantic import BaseModel

class SendMessageSchema(BaseModel):
    content: str | None
    message_type: str
    correlation_id: str | None = None
    
    def __str__(self):
        return json.dumps(self.__dict__)
    
    def __dict__(self):
        return {
            "content": self.content,
            "message_type": self.message_type,
            "correlation_id": self.correlation_id
        }


class Publisher():
    def __init__(self):
        if settings.IS_LOCAL_MESSAGING:
            self.internal_request = settings.INBOX_INTERNAL_REQUEST_URL 
        else:
            # Implement messaging service
            pass
        
    def send_message(self, message: SendMessageSchema):
        if settings.IS_LOCAL_MESSAGING:
            self.__internal_request(message)
        else:
            # Implement messaging service
            pass
    
    def __internal_request(self, message: SendMessageSchema):
        # if message fails (oh well...)
        #TODO: fire and forget
        with httpx.Client() as client:
            try:
                client.post(self.internal_request, data=str(message), headers={"Content-Type": "application/json", "Accept": "application/json"})
                print(f"Message sent: {message}")
            except Exception as e:
                print(f"Failed to send message: {e}")