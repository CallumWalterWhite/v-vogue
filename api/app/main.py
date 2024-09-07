from contextlib import asynccontextmanager
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
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vitonhd.cldm.cldm import ControlLDM
from vitonhd.cldm.model import create_model
from cloth_segmentation.networks import U2NET
from omegaconf import OmegaConf
import torch

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

# TODO: create a schedule list of functions to run with schedule time
def flush_non_sent_messages():
    print(f"Task running at: {time.strftime('%X')}")
    message_flusher = get_message_flusher()
    message_flusher.send_all_messages()

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(flush_non_sent_messages, 'interval', seconds=30)
scheduler.start()

vititonhd_model = None
cloth_segmentation_model = None

device = 'cuda' if torch.cuda.is_available() else 'cpu'


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    session = get_session()
    upgrade_manager = UpgradeManager(session)
    upgrade_manager.run_upgrades()
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(flush_non_sent_messages, 'interval', seconds=10)
    scheduler.start()
    global vititonhd_model, cloth_segmentation_model

    # Load ControlLDM model
    config = OmegaConf.load("path_to_config.yaml")
    vititonhd_model = create_model(config_path=None, config=config)
    checkpoint1 = torch.load("path_to_model_checkpoint.pth", map_location=device)
    vititonhd_model.load_state_dict(checkpoint1["state_dict"])
    vititonhd_model = vititonhd_model.to(device)
    vititonhd_model.eval()

    # Load U2NET model
    cloth_segmentation_model = U2NET(in_ch=3, out_ch=4)
    checkpoint2 = 'trained_checkpoint/checkpoint_u2net.pth'
    if not os.path.isfile(checkpoint2):
        raise FileNotFoundError(f"Checkpoint file not found: {checkpoint2}")
    checkpoint = torch.load(checkpoint2, map_location='cpu')
    cloth_segmentation_model.load_state_dict(checkpoint.get('state_dict', checkpoint), strict=False)
    cloth_segmentation_model = cloth_segmentation_model.to(device)
    cloth_segmentation_model.eval()

    yield
    
    scheduler.shutdown()

app = FastAPI(
    title=settings.PROJECT_NAME,
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan
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
app.include_router(api_router, prefix=settings.API_V1_STR)