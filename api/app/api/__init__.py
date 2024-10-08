from fastapi import APIRouter
from app.api.routes import file_upload, messaging, file_status, run_viton, security

api_router = APIRouter()
api_router.include_router(file_upload.router, tags=["file"]) 
api_router.include_router(messaging.router, tags=["messaging"])
api_router.include_router(file_status.router, tags=["file_status"])
api_router.include_router(run_viton.router, tags=["run_viton"])
api_router.include_router(security.router, tags=["security"])