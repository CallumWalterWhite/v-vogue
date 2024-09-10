from app.models import OutboundMessage
from app.core.deps import SessionDep
import uuid

def get_message_service(session:SessionDep):
    return MessageService(session)

class MessageService:
    def __init__(self, session:SessionDep):
        self.session = session

    def create_message(self, outbound_message:OutboundMessage) -> uuid.UUID:
        self.session.add(outbound_message)
        self.session.flush()
        self.session.commit()
        return outbound_message.id