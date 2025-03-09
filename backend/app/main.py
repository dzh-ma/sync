"""
This module initializes & configures the FastAPI application

It acts as a middleware between the front-end & database, handling:
- API route inclusion
- CORS middleware for front-end communication
- Database initialization & application life-cycle management
"""
import logging
import json
from contextlib import asynccontextmanager
from typing import Any
from bson import ObjectId
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.routes import register_routes
from app.db.database import init_db

# Configure logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
origins = [
    "http://localhost:5173",
    "mongodb://localhost:27017/",
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

    Yields:
        None: Allows FastAPI to manage application life-cycle

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

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

class MongoJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=MongoJSONEncoder,
        ).encode("utf-8")

# Initialize FastAPI application
app = FastAPI(
    title = "Sync Smart Home API",
    description = "API for the Sync Smart Home project",
    version = "1.0.0",
    default_response_class = MongoJSONResponse,
    lifespan = lifespan
)

# Enable CORS for front-end communication
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,    # ["*"] is fine for development but not in production if used
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# Middleware to handle ObjectId in responses
@app.middleware("http")
async def handle_mongodb_objects(request, call_next):
   response = await call_next(request)
   if isinstance(response, Response):
       response.body = json.dumps(
           json.loads(response.body.decode()),
           cls=MongoJSONEncoder
       ).encode()
   return response

# Register all routes
register_routes(app)

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
