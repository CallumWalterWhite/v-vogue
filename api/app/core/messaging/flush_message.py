from sqlmodel import select, Session
from app.core.messaging.publisher import Publisher, SendMessageSchema
from app.models import OutboundMessage

class MessageFlusher(object):
    def __init__(self, session: Session):
        self.__session = session
        self.__publisher = Publisher()
        
    def send_all_messages(self):
        statement = select(OutboundMessage).where(OutboundMessage.is_sent != True)
        session_outbound_messages = self.__session.exec(statement).all()
        for message in session_outbound_messages:
            if message.correlation_id == None:
                send_message_schema = SendMessageSchema(
                    message_type=message.message_type,
                    content=message.content
                    # correlation_id=message.correlation_id
                )
                self.__publisher.send_message(send_message_schema)
                message.is_sent = True
        self.__session.commit()
        self.__session.close()
        
    def send_correlation_id_messages(self, correlation_id: str):
        statement = select(OutboundMessage).where(OutboundMessage.is_sent != True, OutboundMessage.correlation_id == correlation_id)
        session_outbound_messages = self.__session.exec(statement).all()
        for message in session_outbound_messages:
            if message.correlation_id == correlation_id:
                send_message_schema = SendMessageSchema(
                    message_type=message.message_type,
                    content=message.content,
                    correlation_id=correlation_id
                )
                self.__publisher.send_message(send_message_schema)
                message.is_sent = True
        self.__session.commit()
        self.__session.close()
