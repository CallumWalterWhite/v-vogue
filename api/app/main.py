from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.routing import APIRoute
from app.core.messaging.deps import get_message_flusher
from app.core.config import settings
from starlette.middleware.cors import CORSMiddleware
from app.api import api_router
from app.core.middleware.message_flush import MessageFlushMiddleware
from app.core.middleware.auth_middleware import AuthMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from app.upgrade import UpgradeManager
from app.core.deps import get_session
import os
from logging.handlers import RotatingFileHandler
from app.inference import InferenceManager

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

    InferenceManager.setup_all_inference_models(settings)
    
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

app.add_middleware(AuthMiddleware)
app.add_middleware(MessageFlushMiddleware)
app.include_router(api_router, prefix=settings.API_V1_STR)