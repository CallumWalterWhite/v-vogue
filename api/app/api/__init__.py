from fastapi import APIRouter
from app.api.routes import file_upload, messaging

api_router = APIRouter()
api_router.include_router(file_upload.router, tags=["file"]) 
api_router.include_router(messaging.router, tags=["messaging"])