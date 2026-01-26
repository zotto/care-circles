"""
Permission Checking Utilities

Helper functions for checking user permissions on resources.
"""

import logging
from typing import Optional
from fastapi import HTTPException, status
from supabase import Client

from app.middleware.auth import AuthUser

logger = logging.getLogger(__name__)


class PermissionError(HTTPException):
    """Custom exception for permission errors"""
    
    def __init__(self, detail: str = "You don't have permission to access this resource"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


async def check_circle_membership(
    db: Client,
    user: AuthUser,
    circle_id: str
) -> bool:
    """
    Check if user is a member of the specified care circle
    
    Args:
        db: Supabase client
        user: Authenticated user
        circle_id: Care circle ID
        
    Returns:
        bool: True if user is a member
    """
    try:
        result = db.table("care_circle_members").select("id").eq(
            "care_circle_id", circle_id
        ).eq("user_id", user.user_id).execute()
        
        return len(result.data) > 0
    
    except Exception as e:
        logger.error(f"Error checking circle membership: {str(e)}")
        return False


async def check_circle_ownership(
    db: Client,
    user: AuthUser,
    circle_id: str
) -> bool:
    """
    Check if user is the owner of the specified care circle
    
    Args:
        db: Supabase client
        user: Authenticated user
        circle_id: Care circle ID
        
    Returns:
        bool: True if user is the owner
    """
    try:
        result = db.table("care_circles").select("owner_id").eq(
            "id", circle_id
        ).execute()
        
        if not result.data:
            return False
        
        return result.data[0]["owner_id"] == user.user_id
    
    except Exception as e:
        logger.error(f"Error checking circle ownership: {str(e)}")
        return False


async def check_plan_access(
    db: Client,
    user: AuthUser,
    plan_id: str
) -> bool:
    """
    Check if user has access to the specified care plan
    
    Args:
        db: Supabase client
        user: Authenticated user
        plan_id: Care plan ID
        
    Returns:
        bool: True if user has access
    """
    try:
        # Get the plan's circle_id
        plan_result = db.table("care_plans").select(
            "care_circle_id"
        ).eq("id", plan_id).execute()
        
        if not plan_result.data:
            return False
        
        circle_id = plan_result.data[0]["care_circle_id"]
        
        # Check if user is a member of that circle
        return await check_circle_membership(db, user, circle_id)
    
    except Exception as e:
        logger.error(f"Error checking plan access: {str(e)}")
        return False


async def require_circle_membership(
    db: Client,
    user: AuthUser,
    circle_id: str
) -> None:
    """
    Require user to be a member of the specified circle
    
    Args:
        db: Supabase client
        user: Authenticated user
        circle_id: Care circle ID
        
    Raises:
        PermissionError: If user is not a member
    """
    is_member = await check_circle_membership(db, user, circle_id)
    if not is_member:
        raise PermissionError("You must be a member of this care circle")


async def require_circle_ownership(
    db: Client,
    user: AuthUser,
    circle_id: str
) -> None:
    """
    Require user to be the owner of the specified circle
    
    Args:
        db: Supabase client
        user: Authenticated user
        circle_id: Care circle ID
        
    Raises:
        PermissionError: If user is not the owner
    """
    is_owner = await check_circle_ownership(db, user, circle_id)
    if not is_owner:
        raise PermissionError("You must be the owner of this care circle")


async def require_plan_access(
    db: Client,
    user: AuthUser,
    plan_id: str
) -> None:
    """
    Require user to have access to the specified plan
    
    Args:
        db: Supabase client
        user: Authenticated user
        plan_id: Care plan ID
        
    Raises:
        PermissionError: If user doesn't have access
    """
    has_access = await check_plan_access(db, user, plan_id)
    if not has_access:
        raise PermissionError("You don't have access to this care plan")
