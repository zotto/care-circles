"""
Care Task Repository

Database operations for care tasks.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from supabase import Client

from app.db.repositories.base import BaseRepository
from app.config.constants import TaskStatusConstants

logger = logging.getLogger(__name__)


class CareTaskRepository(BaseRepository):
    """Repository for care task operations"""
    
    def __init__(self, db: Client):
        super().__init__(db, "care_tasks")
    
    def get_by_plan(self, plan_id: str) -> List[Dict[str, Any]]:
        """
        Get all tasks for a plan
        
        Args:
            plan_id: Care plan ID
            
        Returns:
            List[dict]: List of tasks
        """
        try:
            result = self.db.table(self.table_name).select("*").eq(
                "care_plan_id", plan_id
            ).order("priority", desc=True).order("created_at").execute()
            
            return result.data
        
        except Exception as e:
            logger.error(f"Error getting tasks by plan: {str(e)}")
            raise
    
    def get_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all tasks claimed by a user
        
        Args:
            user_id: User ID
            
        Returns:
            List[dict]: List of tasks
        """
        try:
            result = self.db.table(self.table_name).select("*").eq(
                "claimed_by", user_id
            ).order("priority", desc=True).order("created_at").execute()
            
            return result.data
        
        except Exception as e:
            logger.error(f"Error getting tasks by user: {str(e)}")
            raise
    
    def get_available_tasks(self) -> List[Dict[str, Any]]:
        """
        Get all available (unclaimed) tasks.
        """
        try:
            result = self.db.table(self.table_name).select("*").eq(
                "status", TaskStatusConstants.AVAILABLE
            ).order("priority", desc=True).order("created_at").execute()
            return result.data
        
        except Exception as e:
            logger.error(f"Error getting available tasks: {str(e)}")
            raise
    
    def claim_task(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Claim a task for a user
        
        Args:
            task_id: Task ID
            user_id: User ID
            
        Returns:
            Optional[dict]: Updated task or None if already claimed
        """
        try:
            # First check if task is available
            task = self.get_by_id(task_id)
            
            if not task:
                raise Exception(f"Task {task_id} not found")
            
            if task["status"] != TaskStatusConstants.AVAILABLE:
                logger.warning(f"Task {task_id} is not available for claiming")
                return None
            
            # Claim the task
            updates = {
                "status": TaskStatusConstants.CLAIMED,
                "claimed_by": user_id,
                "claimed_at": datetime.utcnow().isoformat()
            }
            
            result = self.update(task_id, updates)
            logger.info(f"User {user_id} claimed task {task_id}")
            return result
        
        except Exception as e:
            logger.error(f"Error claiming task: {str(e)}")
            raise
    
    def release_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Release a claimed task back to available
        
        Args:
            task_id: Task ID
            
        Returns:
            Optional[dict]: Updated task or None
        """
        try:
            updates = {
                "status": TaskStatusConstants.AVAILABLE,
                "claimed_by": None,
                "claimed_at": None
            }
            
            result = self.update(task_id, updates)
            logger.info(f"Released task {task_id}")
            return result
        
        except Exception as e:
            logger.error(f"Error releasing task: {str(e)}")
            raise
    
    def complete_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Mark a task as completed

        Args:
            task_id: Task ID

        Returns:
            Optional[dict]: Updated task or None
        """
        try:
            updates = {
                "status": TaskStatusConstants.COMPLETED,
                "completed_at": datetime.utcnow().isoformat()
            }

            result = self.update(task_id, updates)
            logger.info(f"Completed task {task_id}")
            return result

        except Exception as e:
            logger.error(f"Error completing task: {str(e)}")
            raise

    def reopen_task(self, task_id: str, previous_claimed_by: str) -> Optional[Dict[str, Any]]:
        """
        Reopen a completed task and re-assign to the previous owner (claimed_by).
        Sets status to claimed, clears completed_at; claimed_by and claimed_at remain.

        Args:
            task_id: Task ID
            previous_claimed_by: User ID to re-assign (the previous task owner)

        Returns:
            Optional[dict]: Updated task or None
        """
        try:
            updates = {
                "status": TaskStatusConstants.CLAIMED,
                "completed_at": None,
                "claimed_by": previous_claimed_by,
                "claimed_at": datetime.utcnow().isoformat(),
            }
            result = self.update(task_id, updates)
            logger.info(f"Reopened task {task_id}, re-assigned to {previous_claimed_by}")
            return result
        except Exception as e:
            logger.error(f"Error reopening task: {str(e)}")
            raise

    def bulk_create(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create multiple tasks at once
        
        Args:
            tasks: List of task data dictionaries
            
        Returns:
            List[dict]: Created tasks
        """
        try:
            # Add IDs and timestamps to all tasks
            for task in tasks:
                if "id" not in task:
                    from uuid import uuid4
                    task["id"] = str(uuid4())
                if "created_at" not in task:
                    task["created_at"] = datetime.utcnow().isoformat()
            
            result = self.db.table(self.table_name).insert(tasks).execute()
            
            if not result.data:
                raise Exception("Failed to bulk create tasks")
            
            logger.info(f"Bulk created {len(result.data)} tasks")
            return result.data
        
        except Exception as e:
            logger.error(f"Error bulk creating tasks: {str(e)}")
            raise
    
    def update_status_by_plan(
        self,
        plan_id: str,
        new_status: str
    ) -> List[Dict[str, Any]]:
        """
        Update status of all tasks in a plan
        
        Args:
            plan_id: Care plan ID
            new_status: New status for all tasks
            
        Returns:
            List[dict]: Updated tasks
        """
        try:
            updates = {
                "status": new_status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.db.table(self.table_name).update(updates).eq(
                "care_plan_id", plan_id
            ).execute()
            
            logger.info(f"Updated all tasks in plan {plan_id} to status {new_status}")
            return result.data
        
        except Exception as e:
            logger.error(f"Error updating task statuses: {str(e)}")
            raise
