"""
Routes package initializer.
Ensure all routes are properly imported here to be discovered by the main app.
"""
# Import all routes to be registered with the main app
from app.routes.user_routes import router as user_router
from app.routes.profile_routes import router as profile_router
from app.routes.device_routes import router as device_router

# Export routers for use in the main app
__all__ = ["user_router", "profile_router", "device_router"]
