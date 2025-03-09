"""
This module registers all route modules with the FastAPI application
"""

from fastapi import FastAPI

from app.routes.user_routes import router as user_router
from app.routes.data_routes import router as data_router
from app.routes.report_routes import router as report_router
from app.routes.device_routes import router as device_router
from app.routes.profile_routes import router as profile_router
from app.routes.room_routes import router as room_router
from app.routes.schedule_routes import router as schedule_router
from app.routes.summary_routes import router as summary_router

def register_routes(app: FastAPI) -> None:
    """
    Register all route modules with the FastAPI application.
    
    Args:
        app (FastAPI): The FastAPI application instance
    """
    # Include existing routes
    app.include_router(user_router, prefix = "/api/v1/users", tags = ["Users"])
    app.include_router(data_router, prefix = "/api/v1/data", tags = ["Data"])
    app.include_router(report_router, prefix = "/api/v1/reports", tags = ["Reports"])
    
    # Include new routes
    app.include_router(device_router)
    app.include_router(profile_router)
    app.include_router(room_router)
    app.include_router(schedule_router)
    app.include_router(summary_router)
