"""
Care Plans API routes

Handles care plan management and approval.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.middleware.auth import get_current_user, AuthUser
from app.db import get_service_client
from app.services.care_plan_service import CarePlanService
from app.models.domain import CarePlan

logger = logging.getLogger(__name__)

router = APIRouter()


class PlanSummaryUpdate(BaseModel):
    """Request model for updating plan summary"""
    summary: str


class AddTaskToPlanRequest(BaseModel):
    """Request model for adding a task to an existing plan"""
    title: str
    description: str = ""
    category: str = "Other"
    priority: str = "medium"


class CreatePlanRequest(BaseModel):
    """Request model for creating a care plan from a care request"""
    care_request_id: str
    summary: str
    tasks: List[dict]


@router.post(
    "/care-plans",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create care plan",
    description="Create a care plan from a care request with tasks"
)
async def create_care_plan(
    request: CreatePlanRequest,
    user: AuthUser = Depends(get_current_user)
):
    """
    Create a care plan from a care request
    
    Args:
        request: Care plan creation request
        user: Authenticated user from JWT
        
    Returns:
        dict: Created care plan with plan_id
    """
    try:
        db = get_service_client()
        plan_service = CarePlanService(db)
        
        # Get care request to verify it exists and belongs to user
        from app.db.repositories.care_request_repository import CareRequestRepository
        request_repo = CareRequestRepository(db)
        care_request = request_repo.get_by_id(request.care_request_id)
        
        if not care_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Care request not found"
            )
        
        plan = await plan_service.create_plan(
            care_request_id=request.care_request_id,
            created_by=user.user_id,
            summary=request.summary,
            tasks=request.tasks
        )
        
        return {"plan_id": plan["id"], "care_plan": plan}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating care plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create care plan"
        )


@router.get(
    "/care-plans",
    response_model=List[CarePlan],
    summary="List care plans",
    description="List all care plans user has access to"
)
async def list_care_plans(
    user: AuthUser = Depends(get_current_user)
):
    """
    List all care plans user has access to
    
    Returns plans from all care circles the user is a member of.
    
    Args:
        user: Authenticated user from JWT
        
    Returns:
        List[CarePlan]: List of care plans
    """
    try:
        db = get_service_client()
        plan_service = CarePlanService(db)
        
        plans = await plan_service.list_user_plans(user)
        
        return plans
    
    except Exception as e:
        logger.error(f"Error listing care plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list care plans"
        )


@router.get(
    "/care-plans/{plan_id}",
    response_model=dict,
    summary="Get care plan",
    description="Get care plan with tasks"
)
async def get_care_plan(
    plan_id: str,
    user: AuthUser = Depends(get_current_user)
):
    """
    Get care plan with tasks
    
    Args:
        plan_id: Care plan ID
        user: Authenticated user from JWT
        
    Returns:
        dict: Care plan with tasks
    """
    try:
        db = get_service_client()
        plan_service = CarePlanService(db)
        
        plan = await plan_service.get_plan(plan_id, user)
        
        return plan
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting care plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get care plan"
        )


@router.post(
    "/care-plans/{plan_id}/approve",
    response_model=CarePlan,
    summary="Approve care plan",
    description="Approve care plan and make tasks available (creator only)"
)
async def approve_care_plan(
    plan_id: str,
    user: AuthUser = Depends(get_current_user)
):
    """
    Approve care plan (creator only)
    
    Approving a plan transitions all tasks from draft to available status,
    making them claimable by other users.
    
    Args:
        plan_id: Care plan ID
        user: Authenticated user from JWT
        
    Returns:
        CarePlan: Approved care plan
    """
    try:
        db = get_service_client()
        plan_service = CarePlanService(db)
        
        plan = await plan_service.approve_plan(plan_id, user)
        
        return plan
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving care plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve care plan"
        )


@router.get(
    "/care-plans/{plan_id}/tasks",
    response_model=List[dict],
    summary="Get plan tasks",
    description="Get all tasks for a care plan"
)
async def get_plan_tasks(
    plan_id: str,
    user: AuthUser = Depends(get_current_user)
):
    """
    Get all tasks for a care plan
    
    Args:
        plan_id: Care plan ID
        user: Authenticated user from JWT
        
    Returns:
        List[dict]: List of tasks
    """
    try:
        db = get_service_client()
        plan_service = CarePlanService(db)
        
        plan = await plan_service.get_plan(plan_id, user)
        
        return plan.get("tasks", [])
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plan tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get plan tasks"
        )


@router.patch(
    "/care-plans/{plan_id}",
    response_model=CarePlan,
    summary="Update care plan",
    description="Update care plan summary (creator only)"
)
async def update_care_plan(
    plan_id: str,
    updates: PlanSummaryUpdate,
    user: AuthUser = Depends(get_current_user)
):
    """
    Update care plan summary (creator only)
    
    Args:
        plan_id: Care plan ID
        updates: Plan summary update
        user: Authenticated user from JWT
        
    Returns:
        CarePlan: Updated care plan
    """
    try:
        db = get_service_client()
        plan_service = CarePlanService(db)
        
        plan = await plan_service.update_plan_summary(
            plan_id,
            user,
            updates.summary
        )
        
        return plan

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating care plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update care plan"
        )


@router.post(
    "/care-plans/{plan_id}/tasks",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Add task to plan",
    description="Add a task to an existing plan (creator only)"
)
async def add_task_to_plan(
    plan_id: str,
    body: AddTaskToPlanRequest,
    user: AuthUser = Depends(get_current_user)
):
    """
    Add a task to an existing plan (creator only).

    New task is created in draft status.

    Args:
        plan_id: Care plan ID
        body: Task title, description, category, priority
        user: Authenticated user from JWT

    Returns:
        dict: Created task
    """
    try:
        db = get_service_client()
        plan_service = CarePlanService(db)

        task = await plan_service.add_task_to_plan(
            plan_id,
            user,
            body.model_dump()
        )
        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding task to plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add task to plan"
        )


@router.delete(
    "/care-plans/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete care plan",
    description="Delete a care plan and its tasks (creator only)"
)
async def delete_care_plan(
    plan_id: str,
    user: AuthUser = Depends(get_current_user)
):
    """
    Delete a care plan (creator only).

    Tasks are cascade-deleted by the database.

    Args:
        plan_id: Care plan ID
        user: Authenticated user from JWT
    """
    try:
        db = get_service_client()
        plan_service = CarePlanService(db)

        await plan_service.delete_plan(plan_id, user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting care plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete care plan"
        )
