"""
Care Plan Repository

Database operations for care plans.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from supabase import Client

from app.db.repositories.base import BaseRepository
from app.config.constants import PlanStatusConstants

logger = logging.getLogger(__name__)


class CarePlanRepository(BaseRepository):
    """Repository for care plan operations"""
    
    def __init__(self, db: Client):
        super().__init__(db, "care_plans")
    
    def get_by_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get care plan by care request ID
        
        Args:
            request_id: Care request ID
            
        Returns:
            Optional[dict]: Care plan or None
        """
        try:
            result = self.db.table(self.table_name).select("*").eq(
                "care_request_id", request_id
            ).execute()
            
            if not result.data:
                return None
            
            return result.data[0]
        
        except Exception as e:
            logger.error(f"Error getting plan by request: {str(e)}")
            raise
    
    def get_by_circle(self, circle_id: str) -> List[Dict[str, Any]]:
        """
        Get all care plans for a circle
        
        Args:
            circle_id: Care circle ID
            
        Returns:
            List[dict]: List of care plans
        """
        try:
            result = self.db.table(self.table_name).select("*").eq(
                "care_circle_id", circle_id
            ).order("created_at", desc=True).execute()
            
            return result.data
        
        except Exception as e:
            logger.error(f"Error getting plans by circle: {str(e)}")
            raise
    
    def get_by_creator(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all care plans created by a user
        
        Args:
            user_id: User ID
            
        Returns:
            List[dict]: List of care plans
        """
        try:
            result = self.db.table(self.table_name).select("*").eq(
                "created_by", user_id
            ).order("created_at", desc=True).execute()
            
            return result.data
        
        except Exception as e:
            logger.error(f"Error getting plans by creator: {str(e)}")
            raise
    
    def approve_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Approve a care plan
        
        Args:
            plan_id: Care plan ID
            
        Returns:
            dict: Updated plan
        """
        try:
            updates = {
                "status": PlanStatusConstants.APPROVED,
                "approved_at": datetime.utcnow().isoformat()
            }
            
            result = self.update(plan_id, updates)
            
            if not result:
                raise Exception(f"Failed to approve plan {plan_id}")
            
            logger.info(f"Approved care plan {plan_id}")
            return result
        
        except Exception as e:
            logger.error(f"Error approving plan: {str(e)}")
            raise
    
    def get_with_tasks(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get care plan with associated tasks
        
        Args:
            plan_id: Care plan ID
            
        Returns:
            Optional[dict]: Plan with tasks or None
        """
        try:
            # Get plan
            plan = self.get_by_id(plan_id)
            
            if not plan:
                return None
            
            # Get associated tasks
            tasks_result = self.db.table("care_tasks").select("*").eq(
                "care_plan_id", plan_id
            ).order("priority", desc=True).execute()
            
            plan["tasks"] = tasks_result.data
            return plan
        
        except Exception as e:
            logger.error(f"Error getting plan with tasks: {str(e)}")
            raise
