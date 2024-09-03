
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

class MessageFlushMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        logging.info(f"Outbound response status code: {response.status_code}")
        if isinstance(response, Response):
            logging.info(f"Outbound response status code: {response.status_code}")
            response.headers['X-Custom-Header'] = 'CustomValue'
        return response