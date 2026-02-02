"""
Task Service

Business logic for task operations.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status

from supabase import Client
from app.db.repositories.care_task_repository import CareTaskRepository
from app.db.repositories.care_task_event_repository import CareTaskEventRepository
from app.db.repositories.care_plan_repository import CarePlanRepository
from app.db.repositories.care_request_repository import CareRequestRepository
from app.middleware.auth import AuthUser
from app.config.constants import TaskStatusConstants, TaskEventType, TaskEventConstants

logger = logging.getLogger(__name__)


class TaskService:
    """Service for task operations"""

    def __init__(self, db: Client):
        self.db = db
        self.task_repo = CareTaskRepository(db)
        self.event_repo = CareTaskEventRepository(db)
        self.plan_repo = CarePlanRepository(db)
        self.request_repo = CareRequestRepository(db)
    
    async def get_task(
        self,
        task_id: str,
        user: AuthUser
    ) -> Dict[str, Any]:
        """
        Get task by ID
        
        Args:
            task_id: Task ID
            user: Authenticated user
            
        Returns:
            dict: Task
            
        Raises:
            HTTPException: If user doesn't have access
        """
        try:
            task = self.task_repo.get_by_id(task_id)
            
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )
            
            # Access: claimed by user, or plan creator, or care request creator
            if task.get("claimed_by") == user.user_id:
                return task
            plan = self.plan_repo.get_by_id(task["care_plan_id"])
            if plan and plan["created_by"] == user.user_id:
                return task
            req = self.request_repo.get_by_id(task["care_request_id"])
            if req and req["created_by"] == user.user_id:
                return task
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this task"
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting task: {str(e)}")
            raise
    
    async def get_user_tasks(self, user: AuthUser) -> List[Dict[str, Any]]:
        """
        Get all tasks claimed by user
        
        Args:
            user: Authenticated user
            
        Returns:
            List[dict]: List of tasks
        """
        try:
            return self.task_repo.get_by_user(user.user_id)
        
        except Exception as e:
            logger.error(f"Error getting user tasks: {str(e)}")
            raise
    
    async def get_available_tasks(self, user: AuthUser) -> List[Dict[str, Any]]:
        """
        Get available tasks user can claim.
        """
        try:
            return self.task_repo.get_available_tasks()
        
        except Exception as e:
            logger.error(f"Error getting available tasks: {str(e)}")
            raise
    
    async def claim_task(
        self,
        task_id: str,
        user: AuthUser
    ) -> Dict[str, Any]:
        """
        Claim a task for user
        
        Args:
            task_id: Task ID
            user: Authenticated user
            
        Returns:
            dict: Claimed task
            
        Raises:
            HTTPException: If task can't be claimed
        """
        try:
            task = self.task_repo.get_by_id(task_id)
            
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )
            
            # Check if task is available
            if task["status"] != TaskStatusConstants.AVAILABLE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Task is not available for claiming"
                )
            
            # Claim the task
            claimed_task = self.task_repo.claim_task(task_id, user.user_id)
            
            if not claimed_task:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Task was claimed by someone else"
                )
            
            logger.info(f"User {user.user_id} claimed task {task_id}")
            return claimed_task
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error claiming task: {str(e)}")
            raise
    
    async def add_task_status(
        self,
        task_id: str,
        user: AuthUser,
        content: str,
    ) -> Dict[str, Any]:
        """
        Add a status update (diary entry) to a claimed task. Task owner only.

        Args:
            task_id: Task ID
            user: Authenticated user
            content: Status note content

        Returns:
            dict: Created event

        Raises:
            HTTPException: If user doesn't own the task or content invalid
        """
        content_stripped = (content or "").strip()
        if not content_stripped:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status content cannot be empty",
            )
        if len(content_stripped) > TaskEventConstants.MAX_CONTENT_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Content exceeds maximum length of {TaskEventConstants.MAX_CONTENT_LENGTH}",
            )
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        if task.get("claimed_by") != user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the task owner can add status updates",
            )
        event = self.event_repo.create_event(
            care_task_id=task_id,
            event_type=TaskEventType.STATUS_UPDATE,
            content=content_stripped,
            created_by=user.user_id,
        )
        logger.info(f"User {user.user_id} added status to task {task_id}")
        return event

    async def get_task_events(
        self,
        task_id: str,
        user: AuthUser,
    ) -> List[Dict[str, Any]]:
        """
        Get task diary (events). Plan owner or task owner (claimed_by) can view.

        Args:
            task_id: Task ID
            user: Authenticated user

        Returns:
            List[dict]: Events for the task, oldest first
        """
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        is_plan_creator = self._is_plan_creator(task["care_plan_id"], user.user_id)
        is_request_creator = False
        req = self.request_repo.get_by_id(task["care_request_id"])
        if req:
            is_request_creator = req["created_by"] == user.user_id
        is_task_owner = task.get("claimed_by") == user.user_id
        if not (is_plan_creator or is_request_creator or is_task_owner):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this task's diary",
            )
        return self.event_repo.get_by_task(task_id)

    async def release_task(
        self,
        task_id: str,
        user: AuthUser,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Release a claimed task with a reason (recorded in task diary).

        Args:
            task_id: Task ID
            user: Authenticated user
            reason: Reason for releasing (required)

        Returns:
            dict: Released task

        Raises:
            HTTPException: If user doesn't own the task or reason empty
        """
        reason_stripped = (reason or "").strip()
        if not reason_stripped:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide a reason for releasing the task",
            )
        if len(reason_stripped) > TaskEventConstants.MAX_CONTENT_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Reason exceeds maximum length of {TaskEventConstants.MAX_CONTENT_LENGTH}",
            )
        try:
            task = self.task_repo.get_by_id(task_id)

            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found",
                )

            if task.get("claimed_by") != user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only release tasks you have claimed",
                )

            self.event_repo.create_event(
                care_task_id=task_id,
                event_type=TaskEventType.RELEASED,
                content=reason_stripped,
                created_by=user.user_id,
            )
            released_task = self.task_repo.release_task(task_id)

            logger.info(f"User {user.user_id} released task {task_id}")
            return released_task

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error releasing task: {str(e)}")
            raise
    
    async def complete_task(
        self,
        task_id: str,
        user: AuthUser,
        outcome: str,
    ) -> Dict[str, Any]:
        """
        Mark a task as completed with final outcome (recorded in task diary).

        Args:
            task_id: Task ID
            user: Authenticated user
            outcome: Final outcome/status description (required)

        Returns:
            dict: Completed task

        Raises:
            HTTPException: If user doesn't own the task or outcome empty
        """
        outcome_stripped = (outcome or "").strip()
        if not outcome_stripped:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide the final outcome of the task",
            )
        if len(outcome_stripped) > TaskEventConstants.MAX_CONTENT_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Outcome exceeds maximum length of {TaskEventConstants.MAX_CONTENT_LENGTH}",
            )
        try:
            task = self.task_repo.get_by_id(task_id)

            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found",
                )

            if task.get("claimed_by") != user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only complete tasks you have claimed",
                )

            self.event_repo.create_event(
                care_task_id=task_id,
                event_type=TaskEventType.COMPLETED,
                content=outcome_stripped,
                created_by=user.user_id,
            )
            completed_task = self.task_repo.complete_task(task_id)

            logger.info(f"User {user.user_id} completed task {task_id}")
            return completed_task

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error completing task: {str(e)}")
            raise

    async def reopen_task(
        self,
        task_id: str,
        user: AuthUser,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Reopen a completed task (plan owner only). Records reason in task diary and
        re-assigns the task to the previous task owner so they can continue working.

        Args:
            task_id: Task ID
            user: Authenticated user (must be plan owner)
            reason: Reason for reopening (required)

        Returns:
            dict: Reopened task

        Raises:
            HTTPException: If not plan owner, task not completed, or reason empty
        """
        reason_stripped = (reason or "").strip()
        if not reason_stripped:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide a reason for reopening the task",
            )
        if len(reason_stripped) > TaskEventConstants.MAX_CONTENT_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Reason exceeds maximum length of {TaskEventConstants.MAX_CONTENT_LENGTH}",
            )
        try:
            task = self.task_repo.get_by_id(task_id)

            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found",
                )

            if task["status"] != TaskStatusConstants.COMPLETED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only completed tasks can be reopened",
                )

            previous_claimed_by = task.get("claimed_by")
            if not previous_claimed_by:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Task has no previous owner to re-assign",
                )

            if not self._is_plan_creator(task["care_plan_id"], user.user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the plan owner can reopen tasks",
                )

            self.event_repo.create_event(
                care_task_id=task_id,
                event_type=TaskEventType.REOPENED,
                content=reason_stripped,
                created_by=user.user_id,
            )
            reopened_task = self.task_repo.reopen_task(task_id, previous_claimed_by)

            logger.info(
                f"Plan owner {user.user_id} reopened task {task_id}, re-assigned to {previous_claimed_by}"
            )
            return reopened_task

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error reopening task: {str(e)}")
            raise

    async def update_task(
        self,
        task_id: str,
        user: AuthUser,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update task details
        
        Args:
            task_id: Task ID
            user: Authenticated user
            updates: Fields to update
            
        Returns:
            dict: Updated task
            
        Raises:
            HTTPException: If user doesn't have permission
        """
        try:
            task = self.task_repo.get_by_id(task_id)
            
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )
            
            # User can update if they claimed it or created the plan
            can_update = (
                task.get("claimed_by") == user.user_id or
                self._is_plan_creator(task["care_plan_id"], user.user_id)
            )
            
            if not can_update:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to update this task"
                )
            
            # Only allow updating certain fields
            allowed_fields = {"title", "description", "priority", "category"}
            filtered_updates = {
                k: v for k, v in updates.items() if k in allowed_fields
            }
            
            if not filtered_updates:
                return task
            
            return self.task_repo.update(task_id, filtered_updates)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            raise
    
    async def delete_task(
        self,
        task_id: str,
        user: AuthUser
    ) -> None:
        """
        Delete a task (plan creator only).

        Args:
            task_id: Task ID
            user: Authenticated user

        Raises:
            HTTPException: If task not found or user is not the plan creator
        """
        try:
            task = self.task_repo.get_by_id(task_id)

            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )

            if not self._is_plan_creator(task["care_plan_id"], user.user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the plan creator can delete tasks"
                )

            self.task_repo.delete(task_id)
            logger.info(f"User {user.user_id} deleted task {task_id}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting task: {str(e)}")
            raise

    def _is_plan_creator(self, plan_id: str, user_id: str) -> bool:
        """Check if user created the plan"""
        try:
            plan = self.db.table("care_plans").select("created_by").eq(
                "id", plan_id
            ).execute()
            
            if not plan.data:
                return False
            
            return plan.data[0]["created_by"] == user_id
        except Exception:
            return False
