"""
Energy goal management routes for the smart home system.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, Response
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from app.models.goal import (
    CreateEnergyGoal, 
    EnergyGoalDB, 
    EnergyGoalResponse, 
    EnergyGoalUpdate,
    EnergyGoalProgressUpdate,
    GoalType,
    GoalStatus,
    GoalTimeframe
)
# Import at module level for easier patching in tests
from app.db.data import g_c  # Goal collection
from app.core.auth import get_current_user
from app.models.user import UserDB  # For authorization

router = APIRouter(prefix="/goals", tags=["goals"])

@router.get("/", response_model=List[EnergyGoalResponse])
async def get_all_goals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserDB = Depends(get_current_user),
    user_id: Optional[str] = None,
    type: Optional[GoalType] = None,
    status: Optional[GoalStatus] = None,
    timeframe: Optional[GoalTimeframe] = None
) -> List[EnergyGoalResponse]:
    """
    Get all energy goals with filtering options.
    Admin users can see all goals, while regular users can only see their own.
    """
    # Check if user is admin
    if current_user.role != "admin":
        # Non-admin users can only access their own goals
        user_id = current_user.id
    
    # Build query filter
    query: Dict[str, Any] = {}
    if user_id:
        query["user_id"] = user_id
    if type:
        query["type"] = type
    if status:
        query["status"] = status
    if timeframe:
        query["timeframe"] = timeframe
    
    # Convert cursor to list
    cursor = g_c.find(query).skip(skip).limit(limit)
    goals = list(cursor)
    
    # Convert to EnergyGoalResponse models
    return [EnergyGoalResponse.model_validate(goal) for goal in goals]

@router.get("/{goal_id}", response_model=EnergyGoalResponse)
async def get_goal(
    goal_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a single energy goal by ID.
    Users can only access their own goals, while admins can access any goal.
    """
    # Get the goal
    goal = g_c.find_one({"id": goal_id})
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found"
        )
    
    # Check if the requesting user is the goal owner or an admin
    if current_user.role != "admin" and current_user.id != goal["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this goal"
        )
    
    return EnergyGoalResponse.model_validate(goal)

@router.post("/", response_model=EnergyGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_create: CreateEnergyGoal,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Create a new energy goal.
    Users can only create their own goals, while admins can create any goal.
    """
    # Check if the requesting user is the goal owner or an admin
    if current_user.role != "admin" and current_user.id != goal_create.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create goal for another user"
        )
    
    # Create a new EnergyGoalDB model
    goal_db = EnergyGoalDB(**goal_create.model_dump())
    
    # Calculate initial progress percentage
    if goal_db.target_value > 0:
        goal_db.progress_percentage = (goal_db.current_value / goal_db.target_value) * 100
    
    # Insert the goal into the database
    try:
        g_c.insert_one(goal_db.model_dump())
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Goal with this ID already exists"
        )
    
    return EnergyGoalResponse.model_validate(goal_db)

@router.patch("/{goal_id}", response_model=EnergyGoalResponse)
async def update_goal(
    goal_id: str,
    goal_update: EnergyGoalUpdate,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update an energy goal's information.
    Users can only update their own goals, while admins can update any goal.
    """
    # Find the goal to update
    goal = g_c.find_one({"id": goal_id})
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found"
        )
    
    # Check if the requesting user is the goal owner or an admin
    if current_user.role != "admin" and current_user.id != goal["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this goal"
        )
    
    # Create update data dictionary with only the provided fields
    update_data = {k: v for k, v in goal_update.model_dump().items() if v is not None}
    
    # Calculate progress percentage if current_value or target_value is updated
    if "current_value" in update_data or "target_value" in update_data:
        current_value = update_data.get("current_value", goal["current_value"])
        target_value = update_data.get("target_value", goal["target_value"])
        
        if target_value > 0:
            update_data["progress_percentage"] = (current_value / target_value) * 100
    
    # Add updated timestamp
    update_data["updated"] = datetime.utcnow()
    
    # Perform the update if there's data to update
    if update_data:
        try:
            result = g_c.update_one(
                {"id": goal_id},
                {"$set": update_data}
            )
            if result.modified_count == 0 and len(update_data) > 1:  # > 1 to account for the updated timestamp
                raise HTTPException(
                    status_code=status.HTTP_304_NOT_MODIFIED,
                    detail="Goal data not modified"
                )
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update would create a duplicate"
            )
    
    # Retrieve and return the updated goal
    updated_goal = g_c.find_one({"id": goal_id})
    return EnergyGoalResponse.model_validate(updated_goal)

@router.patch("/{goal_id}/progress", response_model=EnergyGoalResponse)
async def update_goal_progress(
    goal_id: str,
    progress_update: EnergyGoalProgressUpdate,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update an energy goal's progress.
    Users can only update their own goals, while admins can update any goal.
    """
    # Find the goal to update
    goal = g_c.find_one({"id": goal_id})
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found"
        )
    
    # Check if the requesting user is the goal owner or an admin
    if current_user.role != "admin" and current_user.id != goal["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this goal"
        )
    
    # Create update data
    current_value = progress_update.current_value
    target_value = goal["target_value"]
    
    update_data = {
        "current_value": current_value,
        "updated": datetime.utcnow()
    }
    
    # Calculate progress percentage
    if target_value > 0:
        update_data["progress_percentage"] = (current_value / target_value) * 100
        
        # Auto-update status if completed
        if current_value >= target_value and goal["status"] == GoalStatus.ACTIVE:
            update_data["status"] = GoalStatus.COMPLETED
    
    # Perform the update
    try:
        result = g_c.update_one(
            {"id": goal_id},
            {"$set": update_data}
        )
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED,
                detail="Goal progress not modified"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating goal progress: {str(e)}"
        )
    
    # Retrieve and return the updated goal
    updated_goal = g_c.find_one({"id": goal_id})
    return EnergyGoalResponse.model_validate(updated_goal)

@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Delete an energy goal.
    Users can only delete their own goals, while admins can delete any goal.
    """
    # Find the goal to delete
    goal = g_c.find_one({"id": goal_id})
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found"
        )
    
    # Check if the requesting user is the goal owner or an admin
    if current_user.role != "admin" and current_user.id != goal["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this goal"
        )
    
    # Perform the deletion
    result = g_c.delete_one({"id": goal_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete goal"
        )
    
    # Return a proper 204 No Content response with no body
    return Response(status_code=status.HTTP_204_NO_CONTENT)
