from fastapi import APIRouter
from app.api.routes import file_upload

api_router = APIRouter()
api_router.include_router(file_upload.router, tags=["file"]) 