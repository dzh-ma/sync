from datetime import datetime
from typing import Optional, Literal
from fastapi import APIRouter, Query, Depends
from app.models.energy_data import EnergyData
from app.db.database import energy_collection
from app.core.security import role_required

router = APIRouter()

@router.post("/add", dependencies = [Depends(role_required("admin"))])
async def add_energy_data(data: EnergyData):
    """API to add new energy data to the database."""
    # energy_collection.insert_one(data.dict())       # Insert into MongoDB
    energy_collection.insert_one(data.model_dump())       # Insert into MongoDB
    return {"message": "Energy data added successfully"}

@router.get("/aggregate")
async def get_aggregated_data(
    start_date: Optional[str] = Query(None, description = "Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description = "End date (YYYY-MM-DD)"),
    device_id: Optional[str] = Query(None, description = "Device ID filter"),
    location: Optional[str] = Query(None, description = "Location filter"),
    interval: Literal["hour", "day", "week"] = "day",
):
    """Fetch aggregated energy data based on filters"""
    query = {}

    if start_date and end_date:
        query["timestamp"] = {
            "$gte": datetime.strptime(start_date, "%Y-%m-%d"),
            "$lte": datetime.strptime(end_date, "%Y-%m-%d")
        }
    if device_id:
        query["device_id"] = device_id
    if location:
        query["location"] = location

    time_group = {
        "year": {"$year": "$timestamp"},
        "month": {"$month": "$timestamp"},
        "day": {"$dayOfMonth": "$timestamp"}
    }

    if interval == "hour":
        time_group = {
            "device_id": "$device_id",
            "year": {"$year": "$timestamp"},
            "month": {"$month": "$timestamp"},
            "day": {"$dayOfMonth": "$timestamp"},
            "hour": {"$hour": "$timestamp"}
        }
    elif interval == "day":
        time_group = {
            "device_id": "$device_id",
            "year": {"$year": "$timestamp"},
            "month": {"$month": "$timestamp"},
            "day": {"$dayOfMonth": "$timestamp"}
        }
    elif interval == "week":
        time_group = {
            "device_id": "$device_id",
            "year": {"$year": "$timestamp"},
            "week": {"$isoWeek": "$timestamp"}
        }

    aggregation_pipeline = [
        {"$match": query},
        {"$group": {
            "_id": {
                "device_id": "$device_id",  # Group by device
                **time_group                # Group by time interval
            }, "total_energy": {"$sum": "$energy_consumed"}
        }}
    ]

    result = list(energy_collection.aggregate(aggregation_pipeline))

    return {"aggregated_data": result}

@router.get("/admin/dashboard", dependencies = [Depends(role_required("admin"))])
async def get_admin_dashboard():
    return {"message": "Welcome, admin!"}
