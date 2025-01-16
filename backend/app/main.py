"""This module acts as a middlepoint between the database and the frontend."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.user_routes import router as user_router
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app_context: FastAPI):
    '''Defines application lifespan event handler'''
    try:
        await init_db()
        app_context.state.custom_attribute = "value"    # Placeholder
        print("Application startup complete.")
        yield
    except Exception as e:
        print(f"Failed to initialize the database: {e}")
        raise e
    finally:
        print("Application is shutting down.")

app = FastAPI(lifespan = lifespan)

# Frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],      # Change `"*"` to specific origins in production
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# Include routers
app.include_router(user_router, prefix = "/api/v1/users", tags = ["Users"])

@app.get("/", response_model = dict)
def read_root() -> dict:
    '''Root endpoint.'''
    return {"message": "Welcome to the Sync Smart Home."}
