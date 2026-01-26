"""
Care Circles API routes

Handles care circle CRUD operations and member management.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.middleware.auth import get_current_user, AuthUser
from app.db import get_service_client
from app.services.care_circle_service import CareCircleService
from app.models.domain import CareCircle

logger = logging.getLogger(__name__)

router = APIRouter()


class CareCircleCreate(BaseModel):
    """Request model for creating a care circle"""
    name: str
    description: str


class CareCircleUpdate(BaseModel):
    """Request model for updating a care circle"""
    name: str | None = None
    description: str | None = None


class AddMemberRequest(BaseModel):
    """Request model for adding a member"""
    user_id: str


@router.post(
    "/care-circles",
    response_model=CareCircle,
    status_code=status.HTTP_201_CREATED,
    summary="Create care circle",
    description="Create a new care circle"
)
async def create_care_circle(
    request: CareCircleCreate,
    user: AuthUser = Depends(get_current_user)
):
    """
    Create a new care circle
    
    The authenticated user becomes the owner of the circle.
    
    Args:
        request: Care circle data
        user: Authenticated user from JWT
        
    Returns:
        CareCircle: Created care circle
    """
    try:
        db = get_service_client()
        circle_service = CareCircleService(db)
        
        circle = await circle_service.create_circle(
            user,
            request.name,
            request.description
        )
        
        return circle
    
    except Exception as e:
        logger.error(f"Error creating care circle: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create care circle"
        )


@router.get(
    "/care-circles",
    response_model=List[CareCircle],
    summary="List care circles",
    description="List all care circles user is a member of"
)
async def list_care_circles(
    user: AuthUser = Depends(get_current_user)
):
    """
    List all care circles user is a member of
    
    Args:
        user: Authenticated user from JWT
        
    Returns:
        List[CareCircle]: List of care circles
    """
    try:
        db = get_service_client()
        circle_service = CareCircleService(db)
        
        circles = await circle_service.list_user_circles(user)
        
        return circles
    
    except Exception as e:
        logger.error(f"Error listing care circles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list care circles"
        )


@router.get(
    "/care-circles/{circle_id}",
    response_model=dict,
    summary="Get care circle",
    description="Get care circle details with members"
)
async def get_care_circle(
    circle_id: str,
    user: AuthUser = Depends(get_current_user)
):
    """
    Get care circle details with members
    
    Args:
        circle_id: Care circle ID
        user: Authenticated user from JWT
        
    Returns:
        dict: Care circle with members
    """
    try:
        db = get_service_client()
        circle_service = CareCircleService(db)
        
        circle = await circle_service.get_circle(circle_id, user)
        
        return circle
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting care circle: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get care circle"
        )


@router.patch(
    "/care-circles/{circle_id}",
    response_model=CareCircle,
    summary="Update care circle",
    description="Update care circle (owner only)"
)
async def update_care_circle(
    circle_id: str,
    updates: CareCircleUpdate,
    user: AuthUser = Depends(get_current_user)
):
    """
    Update care circle (owner only)
    
    Args:
        circle_id: Care circle ID
        updates: Fields to update
        user: Authenticated user from JWT
        
    Returns:
        CareCircle: Updated care circle
    """
    try:
        db = get_service_client()
        circle_service = CareCircleService(db)
        
        circle = await circle_service.update_circle(
            circle_id,
            user,
            updates.model_dump(exclude_unset=True)
        )
        
        return circle
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating care circle: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update care circle"
        )


@router.post(
    "/care-circles/{circle_id}/members",
    status_code=status.HTTP_201_CREATED,
    summary="Add member",
    description="Add a member to care circle (owner only)"
)
async def add_circle_member(
    circle_id: str,
    request: AddMemberRequest,
    user: AuthUser = Depends(get_current_user)
):
    """
    Add a member to care circle (owner only)
    
    Args:
        circle_id: Care circle ID
        request: User ID to add
        user: Authenticated user from JWT
        
    Returns:
        dict: Membership record
    """
    try:
        db = get_service_client()
        circle_service = CareCircleService(db)
        
        member = await circle_service.add_member(
            circle_id,
            request.user_id,
            user
        )
        
        return member
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding circle member: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add member to circle"
        )


@router.delete(
    "/care-circles/{circle_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove member",
    description="Remove a member from care circle (owner only)"
)
async def remove_circle_member(
    circle_id: str,
    user_id: str,
    user: AuthUser = Depends(get_current_user)
):
    """
    Remove a member from care circle (owner only)
    
    Args:
        circle_id: Care circle ID
        user_id: User ID to remove
        user: Authenticated user from JWT
    """
    try:
        db = get_service_client()
        circle_service = CareCircleService(db)
        
        await circle_service.remove_member(circle_id, user_id, user)
        
        return
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing circle member: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove member from circle"
        )
