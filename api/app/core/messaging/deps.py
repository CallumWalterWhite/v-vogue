
from typing import Annotated
from fastapi import Depends
from app.core.deps import get_session 
from app.core.messaging.flush_message import MessageFlusher


def get_message_flusher() -> MessageFlusher:
    session = get_session()
    return MessageFlusher(session)

MessageFlusherDep = Annotated[MessageFlusher, Depends(get_message_flusher)]