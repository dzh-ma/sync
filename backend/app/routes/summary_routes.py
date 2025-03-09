from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from bson.objectid import ObjectId
import pandas as pd

from app.models.energy_summary import EnergySummary
from app.core.security import get_current_user, role_required
from app.db.database import energy_collection, summary_collection, users_collection

router = APIRouter(
    prefix="/api/v1/summaries",
    tags=["Energy Summaries"],
    responses={404: {"description": "Not found"}},
)

@router.post("/generate", dependencies=[Depends(get_current_user)])
async def generate_energy_summary(
    user_id: str, 
    period: str = Query(..., enum=["daily", "weekly", "monthly"]),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Generate an energy consumption summary for the specified period
    
    Args:
        user_id (str): The user ID to generate the summary for
        period (str): The period type (daily, weekly, monthly)
        start_date (Optional[str]): Start date for the summary period (YYYY-MM-DD)
        end_date (Optional[str]): End date for the summary period (YYYY-MM-DD)
        
    Returns:
        dict: The generated energy summary
    
    Raises:
        HTTPException: If generation fails or parameters are invalid
    """
    try:
        # Validate user exists
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Set default dates if not provided
        now = datetime.now(timezone.utc)
        if not end_date:
            end_date = now.date().isoformat()
        
        if not start_date:
            if period == "daily":
                start_date = now.date().isoformat()
            elif period == "weekly":
                start_date = (now - timedelta(days=7)).date().isoformat()
            elif period == "monthly":
                start_date = (now - timedelta(days=30)).date().isoformat()
        
        # Parse dates
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = datetime.fromisoformat(end_date)
        
        if start_datetime > end_datetime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date"
            )
        
        # Query energy data for the period
        query = {
            "timestamp": {
                "$gte": start_datetime,
                "$lte": end_datetime
            }
        }
        
        energy_data = list(energy_collection.find(query))
        
        if not energy_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No energy data available for the selected period"
            )
        
        # Calculate total consumption
        total_consumption = sum(item.get("energy_consumed", 0) for item in energy_data)
        
        # Calculate cost estimate (example rate: $0.15 per kWh)
        cost_estimate = total_consumption * 0.15
        
        # Calculate comparison to previous period
        previous_start = start_datetime - (end_datetime - start_datetime)
        previous_end = start_datetime - timedelta(days=1)
        
        previous_query = {
            "timestamp": {
                "$gte": previous_start,
                "$lte": previous_end
            }
        }
        
        previous_data = list(energy_collection.find(previous_query))
        previous_consumption = sum(item.get("energy_consumed", 0) for item in previous_data) if previous_data else 0
        
        comparison = None
        if previous_consumption > 0:
            comparison = ((total_consumption - previous_consumption) / previous_consumption) * 100
        
        # Create summary object
        summary = EnergySummary(
            user_id=user_id,
            period=period,
            start_date=start_datetime,
            end_date=end_datetime,
            total_consumption=total_consumption,
            cost_estimate=cost_estimate,
            comparison_to_previous=comparison
        )
        
        # Check if summary already exists
        existing_summary = summary_collection.find_one({
            "user_id": user_id,
            "period": period,
            "start_date": start_datetime,
        })
        
        if existing_summary:
            # Update existing summary
            summary_collection.update_one(
                {"_id": existing_summary["_id"]},
                {"$set": summary.model_dump()}
            )
            summary_id = str(existing_summary["_id"])
        else:
            # Insert new summary
            result = summary_collection.insert_one(summary.model_dump())
            summary_id = str(result.inserted_id)
        
        return {
            "message": "Energy summary generated successfully",
            "summary_id": summary_id,
            "summary": summary.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate energy summary: {str(e)}"
        )

@router.get("/", response_model=List[EnergySummary])
async def get_energy_summaries(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    period: Optional[str] = Query(None, description="Filter by period type", enum=["daily", "weekly", "monthly"]),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all energy summaries with optional filtering
    
    Args:
        user_id (Optional[str]): Filter summaries by user ID
        period (Optional[str]): Filter summaries by period type
        current_user (dict): The current authenticated user
        
    Returns:
        List[EnergySummary]: List of energy summaries matching the filter criteria
    """
    query = {}
    if user_id:
        query["user_id"] = user_id
    if period:
        query["period"] = period
        
    summaries = list(summary_collection.find(query))
    
    # Convert ObjectId to string
    for summary in summaries:
        if '_id' in summary:
            summary['_id'] = str(summary['_id'])
            
    return summaries

@router.get("/{summary_id}", response_model=EnergySummary)
async def get_energy_summary(summary_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get a specific energy summary by ID
    
    Args:
        summary_id (str): The ID of the summary to retrieve
        current_user (dict): The current authenticated user
        
    Returns:
        EnergySummary: The requested energy summary
        
    Raises:
        HTTPException: If the summary is not found
    """
    try:
        summary = summary_collection.find_one({"_id": ObjectId(summary_id)})
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Energy summary not found"
            )
        
        # Convert ObjectId to string
        if '_id' in summary:
            summary['_id'] = str(summary['_id'])
            
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving energy summary: {str(e)}"
        )

@router.delete("/{summary_id}", dependencies=[Depends(role_required("admin"))])
async def delete_energy_summary(summary_id: str):
    """
    Delete an energy summary (admin only)
    
    Args:
        summary_id (str): The ID of the summary to delete
        
    Returns:
        dict: Confirmation of deletion
        
    Raises:
        HTTPException: If the summary is not found or deletion fails
    """
    try:
        # Check if summary exists
        summary = summary_collection.find_one({"_id": ObjectId(summary_id)})
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Energy summary not found"
            )
        
        # Delete the summary
        result = summary_collection.delete_one({"_id": ObjectId(summary_id)})
        
        if result.deleted_count:
            return {"message": "Energy summary deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete energy summary"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting energy summary: {str(e)}"
        )
