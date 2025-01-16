"""This module acts as a middlepoint between the database and the frontend."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.user_routes import router as user_router
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app_context: FastAPI):
    '''Defines application lifespan event handler'''
    await init_db()
    app_context.state.custom_attribute = "value"    # Placeholder
    yield
    print("Application is shutting down.")

app = FastAPI(lifespan = lifespan)

# Frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# Include routers
app.include_router(user_router, prefix = "/api/v1/users", tags = ["Users"])

# Root endpoint
@app.get("/")
def read_root():
    '''Startup message.'''
    return {"message": "Welcome to the Sync Smart Home"}


