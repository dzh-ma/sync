from fastapi import FastAPI
from app.routes.user_routes import router as user_router
from app.db.database import init_db

app = FastAPI()

# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()

# Include routers
app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Smart Home Backend"}
