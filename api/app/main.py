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

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

app = FastAPI(
    title=settings.PROJECT_NAME,
    generate_unique_id_function=custom_generate_unique_id,
)

# TODO: create a schedule list of functions to run with schedule time
def flush_non_sent_messages():
    print(f"Task running at: {time.strftime('%X')}")
    message_flusher = get_message_flusher()
    message_flusher.send_all_messages()

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(flush_non_sent_messages, 'interval', seconds=10)
scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    
@app.on_event("startup")
def startup():
    session = get_session()
    upgrade_manager = UpgradeManager(session)
    upgrade_manager.run_upgrades()

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