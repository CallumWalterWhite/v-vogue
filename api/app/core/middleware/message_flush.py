
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.messaging.deps import get_message_flusher, MessageFlusher
from starlette.responses import Response
import logging
import uuid

class MessageFlushMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        correlation_id = uuid.uuid4()
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        message_flusher: MessageFlusher = get_message_flusher()
        message_flusher.send_correlation_id_messages(correlation_id)
        logging.info(f"Outbound response status code: {response.status_code}")
        if isinstance(response, Response):
            logging.info(f"Outbound response status code: {response.status_code}")
            response.headers['X-Custom-Header'] = 'CustomValue'
        return response