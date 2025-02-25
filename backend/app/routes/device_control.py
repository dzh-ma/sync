from fastapi import APIRouter, HTTPException, Depends
from db.database import energy_collection
from models.energy_data import EnergyData
from bson import ObjectId

router = APIRouter()

@router.put("/device/{device_id}/switch")
async def switch_device(device_id: str, status: bool):
    result = energy_collection.update_one(
        {"device_id": device_id},
        {"$set": {"is_on", status}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code = 404, detail = "Device not found, or no change applied.")

    return {"message": f"Device {device_id} turned {"ON" if status else "OFF"}"}
