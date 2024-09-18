from contextlib import asynccontextmanager
import logging
import time
from fastapi import FastAPI
from fastapi.routing import APIRoute
from app.core.messaging.deps import get_message_flusher
from app.core.config import settings
from starlette.middleware.cors import CORSMiddleware
from app.api import api_router
from app.core.middleware.message_flush import MessageFlushMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from app.upgrade import UpgradeManager
from app.core.deps import get_session 
import sys
import os
from logging.handlers import RotatingFileHandler

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

# TODO: create a schedule list of functions to run with schedule time
def flush_non_sent_messages():
    message_flusher = get_message_flusher()
    message_flusher.send_all_messages()

vititonhd_model = None
device = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting app lifespan")
    session = get_session()
    upgrade_manager = UpgradeManager(session)
    upgrade_manager.run_upgrades()
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(flush_non_sent_messages, 'interval', seconds=10)
    scheduler.start()
    global vititonhd_model, device
    #TODO: just rewrite this... it's just bad lol
    import torch
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if settings.LOAD_VITONHD_MODEL:
        from app.inference import setup_vitonHD
        setup_vitonHD(device)
    if settings.LOAD_CLOTH_SEGMENTATION_MODEL == True:
        # Load U2NET model
        from app.inference import setup_cloth_seg
        setup_cloth_seg()
    if settings.LOAD_OPEN_POSE_MODEL == True:
        from app.inference import setup_open_pose
        setup_open_pose()
    if settings.LOAD_HUMAN_PARSING_MODEL == True:
        from app.inference import setup_human_parsing
        setup_human_parsing()
    if settings.LOAD_DENPOSE_MODEL == True:
        from app.inference import setup_densepose
        setup_densepose()

    yield
    
    scheduler.shutdown()

app = FastAPI(
    title=settings.PROJECT_NAME,
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan #uncomment to enable lifespan
)

log_dir = 'log'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file = os.path.join(log_dir, 'app.log')
log_formatter = logging.Formatter(
    '%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
file_handler.setFormatter(log_formatter)
logging.basicConfig(
    level=logging.INFO,
    # handlers=[file_handler]
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(MessageFlushMiddleware)
##TODO: add sqlmodel flusher middleware (flushes all sqlmodel sessions)
app.include_router(api_router, prefix=settings.API_V1_STR)