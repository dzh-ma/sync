from fastapi import APIRouter, Depends, Query
from datetime import datetime
from typing import Optional

from app.models.energy_data import EnergyData
from app.db.database import energy_collection

router = APIRouter()

@router.post("/data/add")
async def add_energy_data(data: EnergyData):
    """API to add new energy data to the database."""
    energy_collection.insert_one(data.dict())       # Insert into MongoDB
    return {"message": "Energy data added successfully"}

@router.get("/data/aggregate")
async def get_aggregated_data(
    start_date: Optional[str] = Query(None, description = "Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description = "End date (YYYY-MM-DD)"),
    device_id: Optional[str] = Query(None, description = "Device ID filter"),
    location: Optional[str] = Query(None, description = "Location filter"),
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

    aggregation_pipeline = [
        {"$match": query},
        {"$group": {"_id": "$device_id", "total_energy": {"$sum": "$energy_consumed"}}}
    ]

    result = list(energy_collection.aggregate(aggregation_pipeline))

    return {"aggregated_data": result}
