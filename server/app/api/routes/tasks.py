"""
Tasks API routes

Handles task claiming, releasing, and management.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from app.middleware.auth import get_current_user, AuthUser
from app.db import get_service_client
from app.services.task_service import TaskService
from app.models.domain import CareTask

logger = logging.getLogger(__name__)

router = APIRouter()


class TaskUpdate(BaseModel):
    """Request model for updating a task"""
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    category: str | None = None


@router.get(
    "/tasks/available",
    response_model=List[CareTask],
    summary="Get available tasks",
    description="Get available tasks that can be claimed"
)
async def get_available_tasks(
    circle_id: str | None = Query(None, description="Filter by care circle ID"),
    user: AuthUser = Depends(get_current_user)
):
    """
    Get available tasks that can be claimed
    
    Args:
        circle_id: Optional circle ID to filter by
        user: Authenticated user from JWT
        
    Returns:
        List[CareTask]: List of available tasks
    """
    try:
        db = get_service_client()
        task_service = TaskService(db)
        
        tasks = await task_service.get_available_tasks(user, circle_id)
        
        return tasks
    
    except Exception as e:
        logger.error(f"Error getting available tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available tasks"
        )


@router.get(
    "/tasks/{task_id}",
    response_model=CareTask,
    summary="Get task",
    description="Get task details"
)
async def get_task(
    task_id: str,
    user: AuthUser = Depends(get_current_user)
):
    """
    Get task details
    
    Args:
        task_id: Task ID
        user: Authenticated user from JWT
        
    Returns:
        CareTask: Task details
    """
    try:
        db = get_service_client()
        task_service = TaskService(db)
        
        task = await task_service.get_task(task_id, user)
        
        return task
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get task"
        )


@router.post(
    "/tasks/{task_id}/claim",
    response_model=CareTask,
    summary="Claim task",
    description="Claim an available task"
)
async def claim_task(
    task_id: str,
    user: AuthUser = Depends(get_current_user)
):
    """
    Claim an available task
    
    Args:
        task_id: Task ID
        user: Authenticated user from JWT
        
    Returns:
        CareTask: Claimed task
    """
    try:
        db = get_service_client()
        task_service = TaskService(db)
        
        task = await task_service.claim_task(task_id, user)
        
        return task
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error claiming task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to claim task"
        )


@router.post(
    "/tasks/{task_id}/release",
    response_model=CareTask,
    summary="Release task",
    description="Release a claimed task back to available"
)
async def release_task(
    task_id: str,
    user: AuthUser = Depends(get_current_user)
):
    """
    Release a claimed task
    
    Args:
        task_id: Task ID
        user: Authenticated user from JWT
        
    Returns:
        CareTask: Released task
    """
    try:
        db = get_service_client()
        task_service = TaskService(db)
        
        task = await task_service.release_task(task_id, user)
        
        return task
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error releasing task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to release task"
        )


@router.post(
    "/tasks/{task_id}/complete",
    response_model=CareTask,
    summary="Complete task",
    description="Mark task as completed"
)
async def complete_task(
    task_id: str,
    user: AuthUser = Depends(get_current_user)
):
    """
    Mark task as completed
    
    Args:
        task_id: Task ID
        user: Authenticated user from JWT
        
    Returns:
        CareTask: Completed task
    """
    try:
        db = get_service_client()
        task_service = TaskService(db)
        
        task = await task_service.complete_task(task_id, user)
        
        return task
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete task"
        )


@router.patch(
    "/tasks/{task_id}",
    response_model=CareTask,
    summary="Update task",
    description="Update task details"
)
async def update_task(
    task_id: str,
    updates: TaskUpdate,
    user: AuthUser = Depends(get_current_user)
):
    """
    Update task details
    
    User can update if they claimed the task or created the plan.
    
    Args:
        task_id: Task ID
        updates: Fields to update
        user: Authenticated user from JWT
        
    Returns:
        CareTask: Updated task
    """
    try:
        db = get_service_client()
        task_service = TaskService(db)
        
        task = await task_service.update_task(
            task_id,
            user,
            updates.model_dump(exclude_unset=True)
        )
        
        return task
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Delete a task (plan creator only)"
)
async def delete_task(
    task_id: str,
    user: AuthUser = Depends(get_current_user)
):
    """
    Delete a task (plan creator only).

    Args:
        task_id: Task ID
        user: Authenticated user from JWT
    """
    try:
        db = get_service_client()
        task_service = TaskService(db)

        await task_service.delete_task(task_id, user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )
