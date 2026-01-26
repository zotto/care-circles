"""
User API routes

Handles user-specific operations like viewing claimed tasks.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth import get_current_user, AuthUser
from app.db import get_service_client
from app.services.task_service import TaskService
from app.models.domain import CareTask

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/users/me/tasks",
    response_model=List[CareTask],
    summary="Get my tasks",
    description="Get all tasks claimed by the current user"
)
async def get_my_tasks(
    user: AuthUser = Depends(get_current_user)
):
    """
    Get all tasks claimed by the current user
    
    Returns tasks across all care circles the user has claimed.
    
    Args:
        user: Authenticated user from JWT
        
    Returns:
        List[CareTask]: List of claimed tasks
    """
    try:
        db = get_service_client()
        task_service = TaskService(db)
        
        tasks = await task_service.get_user_tasks(user)
        
        return tasks
    
    except Exception as e:
        logger.error(f"Error getting user tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get your tasks"
        )
