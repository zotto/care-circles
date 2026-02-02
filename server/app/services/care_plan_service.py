"""
Care Plan Service

Business logic for care plan operations.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status

from supabase import Client
from app.db.repositories.care_plan_repository import CarePlanRepository
from app.db.repositories.care_task_repository import CareTaskRepository
from app.db.repositories.care_circle_repository import CareCircleRepository
from app.middleware.auth import AuthUser
from app.config.constants import PlanStatusConstants, TaskStatusConstants

logger = logging.getLogger(__name__)


class CarePlanService:
    """Service for care plan operations"""
    
    def __init__(self, db: Client):
        self.db = db
        self.plan_repo = CarePlanRepository(db)
        self.task_repo = CareTaskRepository(db)
        self.circle_repo = CareCircleRepository(db)
    
    async def create_plan(
        self,
        care_request_id: str,
        care_circle_id: str,
        created_by: str,
        summary: str,
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a care plan with tasks
        
        This is typically called by the agent pipeline after processing a care request.
        
        Args:
            care_request_id: Care request ID
            care_circle_id: Care circle ID
            created_by: User ID who created the request
            summary: Plan summary
            tasks: List of task data
            
        Returns:
            dict: Created plan with tasks
        """
        try:
            # Create plan
            plan_data = {
                "care_request_id": care_request_id,
                "care_circle_id": care_circle_id,
                "created_by": created_by,
                "summary": summary,
                "status": PlanStatusConstants.DRAFT
            }
            
            plan = self.plan_repo.create(plan_data)
            
            # Add plan_id to all tasks
            for task in tasks:
                task["care_plan_id"] = plan["id"]
                task["care_request_id"] = care_request_id
                task["care_circle_id"] = care_circle_id
                task["status"] = TaskStatusConstants.DRAFT
            
            # Create tasks in bulk
            created_tasks = self.task_repo.bulk_create(tasks)
            
            plan["tasks"] = created_tasks
            
            logger.info(f"Created care plan {plan['id']} with {len(created_tasks)} tasks")
            return plan
        
        except Exception as e:
            logger.error(f"Error creating care plan: {str(e)}")
            raise
    
    async def get_plan(
        self,
        plan_id: str,
        user: AuthUser
    ) -> Dict[str, Any]:
        """
        Get care plan by ID
        
        Args:
            plan_id: Plan ID
            user: Authenticated user
            
        Returns:
            dict: Care plan with tasks
            
        Raises:
            HTTPException: If user doesn't have access
        """
        try:
            plan = self.plan_repo.get_with_tasks(plan_id)
            
            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Care plan not found"
                )
            
            # Check if user has access
            if not self.circle_repo.is_member(plan["care_circle_id"], user.user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this care plan"
                )
            
            return plan
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting care plan: {str(e)}")
            raise
    
    async def list_user_plans(self, user: AuthUser) -> List[Dict[str, Any]]:
        """
        List all plans user has access to
        
        Args:
            user: Authenticated user
            
        Returns:
            List[dict]: List of care plans
        """
        try:
            # Get user's circles
            circles = self.circle_repo.get_user_circles(user.user_id)
            circle_ids = [circle["id"] for circle in circles]
            
            # Get plans for all circles
            all_plans = []
            for circle_id in circle_ids:
                plans = self.plan_repo.get_by_circle(circle_id)
                all_plans.extend(plans)
            
            # Sort by created_at descending
            all_plans.sort(key=lambda p: p["created_at"], reverse=True)
            
            return all_plans
        
        except Exception as e:
            logger.error(f"Error listing user plans: {str(e)}")
            raise
    
    async def approve_plan(
        self,
        plan_id: str,
        user: AuthUser
    ) -> Dict[str, Any]:
        """
        Approve a care plan (creator only)
        
        This transitions tasks from draft to available status.
        
        Args:
            plan_id: Plan ID
            user: Authenticated user
            
        Returns:
            dict: Approved plan
            
        Raises:
            HTTPException: If user is not the creator
        """
        try:
            plan = self.plan_repo.get_by_id(plan_id)
            
            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Care plan not found"
                )
            
            # Only creator can approve
            if plan["created_by"] != user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the plan creator can approve it"
                )
            
            # Check if already approved
            if plan["status"] == PlanStatusConstants.APPROVED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Plan is already approved"
                )
            
            # Approve the plan
            approved_plan = self.plan_repo.approve_plan(plan_id)
            
            # Update all tasks to available status
            self.task_repo.update_status_by_plan(
                plan_id,
                TaskStatusConstants.AVAILABLE
            )
            
            logger.info(f"User {user.user_id} approved plan {plan_id}")
            return approved_plan
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error approving plan: {str(e)}")
            raise
    
    async def update_plan_summary(
        self,
        plan_id: str,
        user: AuthUser,
        summary: str
    ) -> Dict[str, Any]:
        """
        Update plan summary (creator only)
        
        Args:
            plan_id: Plan ID
            user: Authenticated user
            summary: New summary
            
        Returns:
            dict: Updated plan
            
        Raises:
            HTTPException: If user is not the creator
        """
        try:
            plan = self.plan_repo.get_by_id(plan_id)
            
            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Care plan not found"
                )
            
            if plan["created_by"] != user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the plan creator can update it"
                )
            
            return self.plan_repo.update(plan_id, {"summary": summary})

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating plan summary: {str(e)}")
            raise

    async def delete_plan(
        self,
        plan_id: str,
        user: AuthUser
    ) -> None:
        """
        Delete a care plan (creator only).

        Tasks are cascade-deleted by the database.

        Args:
            plan_id: Plan ID
            user: Authenticated user

        Raises:
            HTTPException: If plan not found or user is not the creator
        """
        try:
            plan = self.plan_repo.get_by_id(plan_id)

            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Care plan not found"
                )

            if plan["created_by"] != user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the plan creator can delete it"
                )

            self.plan_repo.delete(plan_id)
            logger.info(f"User {user.user_id} deleted plan {plan_id}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting care plan: {str(e)}")
            raise

    async def add_task_to_plan(
        self,
        plan_id: str,
        user: AuthUser,
        task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add a single task to an existing plan (creator only).

        New task is created in draft status so the owner can adjust before approving.

        Args:
            plan_id: Plan ID
            user: Authenticated user
            task_data: Task fields (title, description, category, priority)

        Returns:
            dict: Created task

        Raises:
            HTTPException: If plan not found or user is not the creator
        """
        try:
            plan = self.plan_repo.get_by_id(plan_id)

            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Care plan not found"
                )

            if plan["created_by"] != user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the plan creator can add tasks"
                )

            task_payload = {
                "care_plan_id": plan_id,
                "care_request_id": plan["care_request_id"],
                "care_circle_id": plan["care_circle_id"],
                "title": task_data.get("title", "").strip() or "New task",
                "description": task_data.get("description", "").strip() or "",
                "category": task_data.get("category", "Other"),
                "priority": task_data.get("priority", "medium"),
                "status": TaskStatusConstants.DRAFT,
            }
            created = self.task_repo.create(task_payload)
            logger.info(f"User {user.user_id} added task to plan {plan_id}")
            return created

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding task to plan: {str(e)}")
            raise
