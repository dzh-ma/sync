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
from app.routes.room_routes import router as room_router
from app.routes.usage_routes import router as usage_router
from app.routes.automation_routes import router as automation_router
from app.routes.notification_routes import router as notification_router
from app.routes.access_management_routes import router as access_management_router
from app.routes.goal_routes import router as goal_router
from app.routes.analytics_routes import router as analytics_router
from app.routes.suggestion_routes import router as suggestion_router
from app.routes.report_routes import router as report_router  # NEW: Import report router

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
    
    # Create reports directory if it doesn't exist
    import os
    from app.utils.report.report_generator import REPORTS_DIR
    os.makedirs(REPORTS_DIR, exist_ok=True)

# Include routers
app.include_router(user_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(device_router, prefix="/api/v1")
app.include_router(room_router, prefix="/api/v1")
app.include_router(usage_router, prefix="/api/v1")
app.include_router(automation_router, prefix="/api/v1")
app.include_router(notification_router, prefix="/api/v1")
app.include_router(access_management_router, prefix="/api/v1")
app.include_router(goal_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(suggestion_router, prefix="/api/v1")
app.include_router(report_router, prefix="/api/v1")  # NEW: Include report router

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
