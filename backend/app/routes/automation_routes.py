"""
Automation management routes for the smart home system.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, Response
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from app.models.automation import CreateAutomation, AutomationDB, AutomationResponse, AutomationDetailResponse, AutomationUpdate, TriggerType, ActionType
# Import at module level for easier patching in tests
from app.db.data import a_c  # Automation collection
from app.core.auth import get_current_user
from app.models.user import UserDB  # For authorization

router = APIRouter(prefix="/automations", tags=["automations"])

@router.get("/", response_model=List[AutomationResponse])
async def get_all_automations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserDB = Depends(get_current_user),
    user_id: Optional[str] = None,
    device_id: Optional[str] = None,
    trigger_type: Optional[TriggerType] = None,
    action_type: Optional[ActionType] = None,
    enabled: Optional[bool] = None
) -> List[AutomationResponse]:
    """
    Get all automations.
    Admin users can see all automations, while regular users can only see their own.
    """
    # Check if user is admin
    if current_user.role != "admin":
        # Non-admin users can only access their own automations
        user_id = current_user.id
    
    # Build query filter
    query: Dict[str, Any] = {}
    if user_id:
        query["user_id"] = user_id
    if device_id:
        query["device_id"] = device_id
    if trigger_type:
        query["trigger_type"] = trigger_type
    if action_type:
        query["action_type"] = action_type
    if enabled is not None:
        query["enabled"] = enabled
    
    # Convert cursor to list
    cursor = a_c.find(query).skip(skip).limit(limit)
    automations = list(cursor)
    
    # Convert to AutomationResponse models
    return [AutomationResponse.model_validate(automation) for automation in automations]

@router.get("/{automation_id}", response_model=AutomationDetailResponse)
async def get_automation(
    automation_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a single automation by ID.
    Users can only access their own automations, while admins can access any automation.
    """
    # Get the automation
    automation = a_c.find_one({"id": automation_id})
    
    if not automation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Automation with ID {automation_id} not found"
        )
    
    # Check if the requesting user is the automation owner or an admin
    if current_user.role != "admin" and current_user.id != automation["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this automation"
        )
    
    return AutomationDetailResponse.model_validate(automation)

@router.post("/", response_model=AutomationDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_automation(
    automation_create: CreateAutomation,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Create a new automation.
    Users can only create automations for themselves, while admins can create for any user.
    """
    # Check if the requesting user is the automation owner or an admin
    if current_user.role != "admin" and current_user.id != automation_create.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create automation for another user"
        )
    
    # Create a new AutomationDB model
    automation_db = AutomationDB(**automation_create.model_dump())
    
    # Insert the automation into the database
    try:
        a_c.insert_one(automation_db.model_dump())
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Automation with this ID already exists"
        )
    
    return AutomationDetailResponse.model_validate(automation_db)

@router.patch("/{automation_id}", response_model=AutomationDetailResponse)
async def update_automation(
    automation_id: str,
    automation_update: AutomationUpdate,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update an automation's information.
    Users can only update their own automations, while admins can update any automation.
    """
    # Find the automation to update
    automation = a_c.find_one({"id": automation_id})
    if not automation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Automation with ID {automation_id} not found"
        )
    
    # Check if the requesting user is the automation owner or an admin
    if current_user.role != "admin" and current_user.id != automation["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this automation"
        )
    
    # Create update data dictionary with only the provided fields
    update_data = {k: v for k, v in automation_update.model_dump().items() if v is not None}
    
    # Add updated timestamp
    update_data["updated"] = datetime.utcnow()
    
    # Perform the update if there's data to update
    if update_data:
        try:
            result = a_c.update_one(
                {"id": automation_id},
                {"$set": update_data}
            )
            if result.modified_count == 0 and len(update_data) > 1:  # > 1 to account for the updated timestamp
                raise HTTPException(
                    status_code=status.HTTP_304_NOT_MODIFIED,
                    detail="Automation data not modified"
                )
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update would create a duplicate entry"
            )
    
    # Retrieve and return the updated automation
    updated_automation = a_c.find_one({"id": automation_id})
    return AutomationDetailResponse.model_validate(updated_automation)

@router.delete("/{automation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_automation(
    automation_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Delete an automation.
    Users can only delete their own automations, while admins can delete any automation.
    """
    # Find the automation to delete
    automation = a_c.find_one({"id": automation_id})
    if not automation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Automation with ID {automation_id} not found"
        )
    
    # Check if the requesting user is the automation owner or an admin
    if current_user.role != "admin" and current_user.id != automation["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this automation"
        )
    
    # Perform the deletion
    result = a_c.delete_one({"id": automation_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete automation"
        )
    
    # Return a proper 204 No Content response with no body
    return Response(status_code=status.HTTP_204_NO_CONTENT)
