"""
This module defines API routes for managing & retrieving energy consumption data

It includes:
- An endpoint for adding new energy data (admin-only access)
- An endpoint for fetching aggregated energy consumption data with filtering options
- An admin dashboard route (restricted to users with an "admin" role)
"""
from datetime import datetime
from typing import Optional, Literal, List
from pymongo import ASCENDING
from fastapi import APIRouter, Query, Depends, HTTPException
from app.models.energy_data import EnergyData
from app.db.database import energy_collection
from app.core.security import role_required

router = APIRouter()

@router.post("/add", dependencies = [Depends(role_required("admin"))])
async def add_energy_data(data: EnergyData) -> dict:
    """
    Add new energy consumption data to the database (admin-only)

    Args:
        data (EnergyData): The energy data record to be added

    Returns:
        dict: A confirmation message upon successfully insertion
    """
    timestamp = datetime.utcnow()

    result = energy_collection.update_one(
        {"device_id": data.device_id},
        {
            "$push": {
                "timestamps": timestamp,
                "energy_consumed": data.energy_consumed
            },
            "$setOnInsert": {"location": data.location, "created_at": timestamp}
        },
        upsert = True   # Create document if it doesn't exist
    )
    # energy_collection.insert_one(data.model_dump())       # Insert into MongoDB
    if result.modified_count > 0 or result.upserted_id:
        return {"message": f"Energy data added successfully for device {data.device_id}."}
    else:
        raise HTTPException(status_code = 500, detail = "Failed to update energy data.")

@router.get("/aggregate")
async def get_aggregated_data(
    start_date: Optional[str] = Query(None, description = "Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description = "End date (YYYY-MM-DD)"),
    device_id: Optional[str] = Query(None, description = "Device ID filter"),
    location: Optional[str] = Query(None, description = "Location filter"),
    interval: Literal["hour", "day", "week"] = "day",
) -> dict:
    """
    Retrieve aggregated energy consumption data based on time interval & filters

    Args:
        start_date (Optional[str]): The start date for filtering (YYYY-MM-DD)
        end_date (Optional[str]): The end date for filtering (YYYY-MM-DD)
        device_id (Optional[str]): The ID of the device to filter data
        location (Optional[str]): The location filter
        interval (Literal["hour", "day", "week"]): The time interval for aggregation (defaults to "day")

    Returns:
        dict: Aggregated energy consumption data grouped by the selected interval
    """
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
async def get_admin_dashboard() -> dict:
    """
    Admin dashboard endpoint (restricted access)

    Returns:
        dict: A welcome message confirming admin access
    """
    return {"message": "Welcome, admin!"}

# NOTE: Missing docstring
@router.get("/energy/usage")
async def get_energy_usage(
        device_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
) -> List[dict]:
    query = {}

    if device_id:
        query["device_id"] = device_id

    if start_date and end_date:
        query["timestamps"] = {
            "$gte": datetime.strptime(start_date, "%Y-%m-%d"),
            "$lte": datetime.strptime(end_date, "%Y-%m-%d")
        }

    results = energy_collection.find(query).sort("timestamps", ASCENDING)
    return [{"device_id": r["device_id"], "timestamps": r["timestamps"], "energy_consumed": r["energy_consumed"]} for r in results]
