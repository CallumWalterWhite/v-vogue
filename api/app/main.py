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

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

# TODO: create a schedule list of functions to run with schedule time
def flush_non_sent_messages():
    print(f"Task running at: {time.strftime('%X')}")
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
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    #TODO: just rewrite this... it's just bad lol
    import torch
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if settings.LOAD_VITONHD_MODEL:
        # Improve performance by importing the models only when needed
        from vitonhd.cldm.model import create_model
        from cloth_segmentation.cloth_segmentation.networks import U2NET
        from omegaconf import OmegaConf
        # Load ControlLDM model
        config = OmegaConf.load(settings.VITONHD_MODEL_CONFIG_PATH)
        vititonhd_model = create_model(config_path=None, config=config)
        load_cp = torch.load(settings.VITONHD_MODEL_PATH, map_location=device)
        load_cp = load_cp["state_dict"] if "state_dict" in load_cp.keys() else load_cp
        vititonhd_model.load_state_dict(load_cp)
        vititonhd_model = vititonhd_model.cuda()
        vititonhd_model.eval()
    if settings.LOAD_CLOTH_SEGMENTATION_MODEL:
        # Load U2NET model
        from app.inference import setup_cloth_seg
        setup_cloth_seg()
    if settings.LOAD_OPEN_POSE_MODEL:
        from app.inference import setup_open_pose
        setup_open_pose()
    
    yield
    
    scheduler.shutdown()

app = FastAPI(
    title=settings.PROJECT_NAME,
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan #uncomment to enable lifespan
)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
    
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