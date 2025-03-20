"""
Main application entry point for the smart home API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import database initialization
from app.db.data import init_db

# Import routers
from app.routes.user_routes import router as user_router
from app.routes.profile_routes import router as profile_router
from app.routes.device_routes import router as device_router
# Import other routers here

# Create FastAPI application
app = FastAPI(
    title="Sync Smart Home API",
    description="API for managing the Sync smart home system",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add event handlers for startup
@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    init_db()

# Include routers
app.include_router(user_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(device_router, prefix="/api/v1")

# Add a root endpoint for API health check
@app.get("/")
async def root():
    """
    API health check endpoint.
    """
    return {
        "status": "online",
        "message": "Sync Smart Home API is running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
