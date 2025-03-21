"""
This module initializes & configures the FastAPI application

It acts as a middleware between the front-end & database, handling:
- API route inclusion
- CORS middleware for front-end communication
- Database initialization & application life-cycle management
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .routes.user_routes import router as user_router
from .routes.data_routes import router as data_router
from .routes.report_routes import router as report_router
from .routes.device_routes import router as device_router
from .routes.profile_routes import router as profile_router
from .routes.room_routes import router as room_router
from .routes.summary_routes import router as summary_router
from .routes.schedule_routes import router as schedule_router
from .db.database import init_db

# Configure logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
origins = [
    "http://localhost:5173",
    "mongodb://localhost:27017/",
    "http://localhost:3000"
    "http://localhost:3000"
]

@asynccontextmanager
async def lifespan(app_context: FastAPI):
    """
    Defines application's lifespan event handler

    - Initialization the database at startup
    - Sets up application-wide state variables
    - Logs startup & shutdown events

    Args:
        app_context (FastAPI): The FastAPI application instance

    Raises:
        Exception: If database initialization fails
    """
    try:
        await init_db()
        app_context.state.custom_attribute = "value"    # Placeholder for future app-wide state
        logger.info("Application startup complete.")
        yield
    except Exception as e:
        logger.error("Failed to initialize the database: %e.")
        raise e
    finally:
        logger.info("Application is shutting down.")

# Initialize FastAPI application
app = FastAPI(lifespan = lifespan)

# Enable CORS for front-end communication
app.add_middleware(
    CORSMiddleware,
    # allow_origins = ALLOWED_ORIGINS,      # Change `"*"` to specific origins/domain in production
    allow_origins = ["*"],      # Change `"*"` to specific origins/domain in production
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# Include API routers
app.include_router(user_router, prefix = "/api/v1/users", tags = ["Users"])
app.include_router(data_router, prefix = "/api/v1/data", tags = ["Data"])
app.include_router(report_router, tags = ["Reports"])
# app.include_router(device_router, prefix = "/api/v1/devices", tags = ["Devices"])
# app.include_router(profile_router, prefix = "/api/v1/profiles", tags = ["Profiles"])
# app.include_router(room_router, prefix = "/api/v1/rooms", tags = ["Rooms"])
# app.include_router(schedule_router, prefix = "/api/v1/schedules", tags = ["Schedule"])
# app.include_router(summary_router, prefix = "/api/v1/summaries", tags = ["Summary"])
app.include_router(device_router)
app.include_router(profile_router)
app.include_router(room_router)
app.include_router(schedule_router)
app.include_router(summary_router)

# Root response model
class RootResponse(BaseModel):
    """
    Response model for the root endpoint

    Attributes:
        message (str): Welcome message
    """
    message: str

@app.get("/", response_model = RootResponse)
def read_root() -> RootResponse:
    """
    Root endpoint

    Returns:
        RootResponse: A welcome message for the API
    """
    return RootResponse(message = "Welcome to the Sync Smart Home.")
