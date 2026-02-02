"""
Task Service

Business logic for task operations.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status

from supabase import Client
from app.db.repositories.care_task_repository import CareTaskRepository
from app.db.repositories.care_circle_repository import CareCircleRepository
from app.middleware.auth import AuthUser
from app.config.constants import TaskStatusConstants

logger = logging.getLogger(__name__)


class TaskService:
    """Service for task operations"""
    
    def __init__(self, db: Client):
        self.db = db
        self.task_repo = CareTaskRepository(db)
        self.circle_repo = CareCircleRepository(db)
    
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
            
            # Check if user has access (member of circle or claimed the task)
            has_access = (
                self.circle_repo.is_member(task["care_circle_id"], user.user_id) or
                task.get("claimed_by") == user.user_id
            )
            
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this task"
                )
            
            return task
        
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
    
    async def get_available_tasks(
        self,
        user: AuthUser,
        circle_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get available tasks user can claim
        
        Args:
            user: Authenticated user
            circle_id: Optional circle ID to filter by
            
        Returns:
            List[dict]: List of available tasks
        """
        try:
            tasks = self.task_repo.get_available_tasks(circle_id)
            
            # Filter to only tasks in circles user is a member of
            accessible_tasks = []
            for task in tasks:
                if self.circle_repo.is_member(task["care_circle_id"], user.user_id):
                    accessible_tasks.append(task)
            
            return accessible_tasks
        
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
    
    async def release_task(
        self,
        task_id: str,
        user: AuthUser
    ) -> Dict[str, Any]:
        """
        Release a claimed task
        
        Args:
            task_id: Task ID
            user: Authenticated user
            
        Returns:
            dict: Released task
            
        Raises:
            HTTPException: If user doesn't own the task
        """
        try:
            task = self.task_repo.get_by_id(task_id)
            
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )
            
            # Check if user owns the task
            if task.get("claimed_by") != user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only release tasks you have claimed"
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
        user: AuthUser
    ) -> Dict[str, Any]:
        """
        Mark a task as completed
        
        Args:
            task_id: Task ID
            user: Authenticated user
            
        Returns:
            dict: Completed task
            
        Raises:
            HTTPException: If user doesn't own the task
        """
        try:
            task = self.task_repo.get_by_id(task_id)
            
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )
            
            # Check if user owns the task
            if task.get("claimed_by") != user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only complete tasks you have claimed"
                )
            
            completed_task = self.task_repo.complete_task(task_id)
            
            logger.info(f"User {user.user_id} completed task {task_id}")
            return completed_task
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error completing task: {str(e)}")
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
