"""
This module defines API routes for energy consumption summaries
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from app.utils.data_operations import (
    generate_energy_summary,
    get_user_energy_summaries
)
from app.core.security import get_current_user, role_required, profile_permission_required
from app.db.database import summary_collection
from bson import ObjectId

router = APIRouter(
    prefix="/api/v1/summaries",
    tags=["summaries"],
    responses={404: {"description": "Not found"}},
)

@router.post("/generate")
async def generate_summary(
    user_id: str = Query(..., description="User ID to generate summary for"),
    period: str = Query("daily", description="Period type (daily, weekly, monthly)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    current_user: dict = Depends(profile_permission_required("can_access_energy_data"))
):
    """
    Generate an energy consumption summary
    
    Args:
        user_id (str): User ID to generate summary for
        period (str): Period type (daily, weekly, monthly)
        start_date (Optional[str]): Start date (YYYY-MM-DD)
        
    Returns:
        dict: The generated summary with ID
    """
    # Only allow generating summaries for your own user_id unless admin
    if user_id != current_user.get("sub") and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only generate summaries for your own account"
        )
    
    # Parse start_date if provided, otherwise use current date
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid date format. Use YYYY-MM-DD."
            )
    else:
        start_date_obj = datetime.now()
    
    # Calculate end_date based on period
    if period == "daily":
        end_date_obj = start_date_obj + timedelta(days=1)
    elif period == "weekly":
        end_date_obj = start_date_obj + timedelta(days=7)
    elif period == "monthly":
        # Approximate a month as 30 days
        end_date_obj = start_date_obj + timedelta(days=30)
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid period. Use 'daily', 'weekly', or 'monthly'."
        )
    
    # Generate the summary
    summary = await generate_energy_summary(
        user_id=user_id,
        period=period,
        start_date=start_date_obj,
        end_date=end_date_obj
    )
    
    # Insert into database to match test expectations
    result = summary_collection.insert_one(summary)
    summary_id = str(result.inserted_id)
    
    return {
        "message": "Energy summary generated successfully",
        "summary_id": summary_id,
        "summary": summary
    }

@router.get("/")
async def get_summaries(
    period: Optional[str] = Query(None, description="Filter by period (daily, weekly, monthly)"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    current_user: dict = Depends(profile_permission_required("can_access_energy_data"))
):
    """
    Get energy summaries, optionally filtered by period or user
    
    Args:
        period (Optional[str]): Filter by period type
        user_id (Optional[str]): Filter by user ID
        
    Returns:
        list: A list of energy summaries
    """
    # If user_id is provided, only allow access to your own summaries unless admin
    if user_id and user_id != current_user.get("sub") and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only access your own summaries"
        )
    
    # Default to the current user's ID if no user_id is provided
    actual_user_id = user_id if user_id else current_user.get("sub")
    
    # Get summaries
    return await get_user_energy_summaries(actual_user_id, period)

@router.get("/{summary_id}")
async def get_summary_by_id(
    summary_id: str,
    current_user: dict = Depends(profile_permission_required("can_access_energy_data"))
):
    """
    Get a specific energy summary by ID
    
    Args:
        summary_id (str): The ID of the summary to retrieve
        
    Returns:
        dict: The summary data
    """
    try:
        summary = summary_collection.find_one({"_id": ObjectId(summary_id)})
        
        if not summary:
            raise HTTPException(
                status_code=404,
                detail=f"Summary with ID {summary_id} not found"
            )
        
        # Ensure users can only access their own summaries unless they're admin
        if summary.get("user_id") != current_user.get("sub") and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="You can only access your own summaries"
            )
        
        # Convert ObjectId to string
        summary["_id"] = str(summary["_id"])
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving summary: {str(e)}"
        )

@router.delete("/{summary_id}")
async def delete_summary(
    summary_id: str,
    current_user: dict = Depends(role_required("admin"))
):
    """
    Delete an energy summary (admin only)
    
    Args:
        summary_id (str): The ID of the summary to delete
        
    Returns:
        dict: A success message
    """
    try:
        summary = summary_collection.find_one({"_id": ObjectId(summary_id)})
        
        if not summary:
            raise HTTPException(
                status_code=404,
                detail=f"Summary with ID {summary_id} not found"
            )
        
        # Delete the summary
        result = summary_collection.delete_one({"_id": ObjectId(summary_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete summary with ID {summary_id}"
            )
        
        return {"message": "Energy summary deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting summary: {str(e)}"
        )
