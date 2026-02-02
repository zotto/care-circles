"""
Tasks API routes

Handles task claiming, releasing, completion, and task diary (events).
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.middleware.auth import get_current_user, AuthUser
from app.db import get_service_client
from app.services.task_service import TaskService
from app.models.domain import CareTask, CareTaskEvent
from app.config.constants import TaskEventConstants

logger = logging.getLogger(__name__)

router = APIRouter()


class TaskUpdate(BaseModel):
    """Request model for updating a task"""
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    category: str | None = None


class TaskStatusAddBody(BaseModel):
    """Request body for adding a status update to a task"""
    content: str = Field(..., min_length=1, max_length=TaskEventConstants.MAX_CONTENT_LENGTH)


class TaskCompleteBody(BaseModel):
    """Request body for completing a task with outcome"""
    outcome: str = Field(..., min_length=1, max_length=TaskEventConstants.MAX_CONTENT_LENGTH)


class TaskReleaseBody(BaseModel):
    """Request body for releasing a task with reason"""
    reason: str = Field(..., min_length=1, max_length=TaskEventConstants.MAX_CONTENT_LENGTH)


@router.get(
    "/tasks/available",
    response_model=List[CareTask],
    summary="Get available tasks",
    description="Get available tasks that can be claimed"
)
async def get_available_tasks(
    user: AuthUser = Depends(get_current_user)
):
    """
    Get available tasks that can be claimed.
    """
    try:
        db = get_service_client()
        task_service = TaskService(db)
        tasks = await task_service.get_available_tasks(user)
        
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
    description="Release a claimed task with a reason (recorded in task diary)",
)
async def release_task(
    task_id: str,
    body: TaskReleaseBody,
    user: AuthUser = Depends(get_current_user),
):
    """
    Release a claimed task with a reason. Reason is stored in the task diary.

    Args:
        task_id: Task ID
        body: Must include reason
        user: Authenticated user from JWT

    Returns:
        CareTask: Released task
    """
    try:
        db = get_service_client()
        task_service = TaskService(db)

        task = await task_service.release_task(task_id, user, body.reason)

        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error releasing task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to release task",
        )


@router.post(
    "/tasks/{task_id}/complete",
    response_model=CareTask,
    summary="Complete task",
    description="Mark task as completed with final outcome (recorded in task diary)",
)
async def complete_task(
    task_id: str,
    body: TaskCompleteBody,
    user: AuthUser = Depends(get_current_user),
):
    """
    Mark task as completed with final outcome. Outcome is stored in the task diary.

    Args:
        task_id: Task ID
        body: Must include outcome
        user: Authenticated user from JWT

    Returns:
        CareTask: Completed task
    """
    try:
        db = get_service_client()
        task_service = TaskService(db)

        task = await task_service.complete_task(task_id, user, body.outcome)

        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete task",
        )


@router.post(
    "/tasks/{task_id}/events",
    response_model=CareTaskEvent,
    summary="Add status update",
    description="Add a status/progress note to a claimed task (task diary)",
)
async def add_task_status(
    task_id: str,
    body: TaskStatusAddBody,
    user: AuthUser = Depends(get_current_user),
):
    """
    Add a status update to a task you own. Visible to plan owner for follow-up.

    Args:
        task_id: Task ID
        body: Must include content
        user: Authenticated user from JWT

    Returns:
        CareTaskEvent: Created event
    """
    try:
        db = get_service_client()
        task_service = TaskService(db)

        event = await task_service.add_task_status(task_id, user, body.content)

        return event

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding task status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add status",
        )


@router.get(
    "/tasks/{task_id}/events",
    response_model=List[CareTaskEvent],
    summary="Get task diary",
    description="Get task events (status updates, completion outcome, release reason)",
)
async def get_task_events(
    task_id: str,
    user: AuthUser = Depends(get_current_user),
):
    """
    Get task diary (events). Plan owner or task owner can view.

    Args:
        task_id: Task ID
        user: Authenticated user from JWT

    Returns:
        List[CareTaskEvent]: Events for the task, oldest first
    """
    try:
        db = get_service_client()
        task_service = TaskService(db)

        events = await task_service.get_task_events(task_id, user)

        return events

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get task diary",
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
