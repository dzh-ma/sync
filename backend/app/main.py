"""This module acts as a middlepoint between the database and the frontend."""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.routes.user_routes import router as user_router
from app.routes.data_routes import router as data_router
from app.db.database import init_db

# Configure logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

@asynccontextmanager
async def lifespan(app_context: FastAPI):
    """Defines application lifespan event handler"""
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

app = FastAPI(lifespan = lifespan)

# Front-end communication
app.add_middleware(
    CORSMiddleware,
    allow_origins = ALLOWED_ORIGINS,      # Change `"*"` to specific origins/domain in production
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# Include routers
app.include_router(user_router, prefix = "/api/v1/users", tags = ["Users"])
app.include_router(data_router, prefix = "/api/v1/data", tags = ["Data"])

# Root response model
class RootResponse(BaseModel):
    message: str

@app.get("/", response_model = RootResponse)
def read_root() -> RootResponse:
    """Root endpoint."""
    return RootResponse(message = "Welcome to the Sync Smart Home.")
