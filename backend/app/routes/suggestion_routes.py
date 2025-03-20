"""
Suggestion management routes for the smart home system.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, Response
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from app.models.suggestion import CreateSuggestion, SuggestionDB, SuggestionResponse, SuggestionUpdate, SuggestionStatus, SuggestionType
# Import at module level for easier patching in tests
from app.db.data import s_c  # Suggestion collection
from app.core.auth import get_current_user
from app.models.user import UserDB  # For authorization

router = APIRouter(prefix="/suggestions", tags=["suggestions"])

@router.get("/", response_model=List[SuggestionResponse])
async def get_all_suggestions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserDB = Depends(get_current_user),
    user_id: Optional[str] = None,
    status: Optional[SuggestionStatus] = None,
    type: Optional[SuggestionType] = None,
    priority: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> List[SuggestionResponse]:
    """
    Get all suggestions.
    Admin users can see all suggestions, while regular users can only see their own.
    """
    # Check if user is admin
    if current_user.role != "admin":
        # Non-admin users can only access their own suggestions
        user_id = current_user.id
    
    # Build query filter
    query: Dict[str, Any] = {}
    if user_id:
        query["user_id"] = user_id
    if status:
        query["status"] = status
    if type:
        query["type"] = type
    if priority:
        query["priority"] = priority
    
    # Date range filtering
    if from_date or to_date:
        date_query = {}
        if from_date:
            date_query["$gte"] = from_date
        if to_date:
            date_query["$lte"] = to_date
        if date_query:
            query["created"] = date_query
    
    # Convert cursor to list
    cursor = s_c.find(query).skip(skip).limit(limit).sort("created", -1)
    suggestions = list(cursor)
    
    # Convert to SuggestionResponse models
    return [SuggestionResponse.model_validate(suggestion) for suggestion in suggestions]

@router.get("/{suggestion_id}", response_model=SuggestionResponse)
async def get_suggestion(
    suggestion_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a single suggestion by ID.
    Users can only access their own suggestions, while admins can access any suggestion.
    """
    # Get the suggestion
    suggestion = s_c.find_one({"id": suggestion_id})
    
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suggestion with ID {suggestion_id} not found"
        )
    
    # Check if the requesting user is the suggestion owner or an admin
    if current_user.role != "admin" and current_user.id != suggestion["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this suggestion"
        )
    
    return SuggestionResponse.model_validate(suggestion)

@router.post("/", response_model=SuggestionResponse, status_code=status.HTTP_201_CREATED)
async def create_suggestion(
    suggestion_create: CreateSuggestion,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Create a new suggestion.
    Users can only create suggestions for themselves, while admins can create suggestions for any user.
    """
    # Check if the requesting user is the suggestion owner or an admin
    if current_user.role != "admin" and current_user.id != suggestion_create.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create suggestion for another user"
        )
    
    # Create a new SuggestionDB model
    suggestion_db = SuggestionDB(**suggestion_create.model_dump())
    
    # Insert the suggestion into the database
    try:
        s_c.insert_one(suggestion_db.model_dump())
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Suggestion with this ID already exists"
        )
    
    return SuggestionResponse.model_validate(suggestion_db)

@router.patch("/{suggestion_id}", response_model=SuggestionResponse)
async def update_suggestion(
    suggestion_id: str,
    suggestion_update: SuggestionUpdate,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update a suggestion's information.
    Users can only update their own suggestions, while admins can update any suggestion.
    """
    # Find the suggestion to update
    suggestion = s_c.find_one({"id": suggestion_id})
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suggestion with ID {suggestion_id} not found"
        )
    
    # Check if the requesting user is the suggestion owner or an admin
    if current_user.role != "admin" and current_user.id != suggestion["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this suggestion"
        )
    
    # Create update data dictionary with only the provided fields
    update_data = {k: v for k, v in suggestion_update.model_dump().items() if v is not None}
    
    # Update implemented_date if status is changed to IMPLEMENTED
    if suggestion_update.status == SuggestionStatus.IMPLEMENTED:
        update_data["implemented_date"] = datetime.utcnow()
    
    # Add updated timestamp
    update_data["updated"] = datetime.utcnow()
    
    # Perform the update if there's data to update
    if update_data:
        try:
            result = s_c.update_one(
                {"id": suggestion_id},
                {"$set": update_data}
            )
            if result.modified_count == 0 and len(update_data) > 1:  # > 1 to account for the updated timestamp
                raise HTTPException(
                    status_code=status.HTTP_304_NOT_MODIFIED,
                    detail="Suggestion data not modified"
                )
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update would create a duplicate"
            )
    
    # Retrieve and return the updated suggestion
    updated_suggestion = s_c.find_one({"id": suggestion_id})
    return SuggestionResponse.model_validate(updated_suggestion)

@router.delete("/{suggestion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_suggestion(
    suggestion_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Delete a suggestion.
    Users can only delete their own suggestions, while admins can delete any suggestion.
    """
    # Find the suggestion to delete
    suggestion = s_c.find_one({"id": suggestion_id})
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suggestion with ID {suggestion_id} not found"
        )
    
    # Check if the requesting user is the suggestion owner or an admin
    if current_user.role != "admin" and current_user.id != suggestion["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this suggestion"
        )
    
    # Perform the deletion
    result = s_c.delete_one({"id": suggestion_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete suggestion"
        )
    
    # Return a proper 204 No Content response with no body
    return Response(status_code=status.HTTP_204_NO_CONTENT)
