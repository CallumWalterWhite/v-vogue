from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

ALLOWED_PATHS = ["/login/google", "/auth/google/callback", "/login/facebook", "/auth/facebook/callback"]
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if settings.DISABLE_AUTH:
            return await call_next(request)
        if any(request.url.path.startswith(path) for path in ALLOWED_PATHS):
            return await call_next(request)
        token = request.headers.get("Authorization")
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Unauthorized"}
            )

        response = await call_next(request)
        return response