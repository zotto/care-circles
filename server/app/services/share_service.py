"""
Share Service

Business logic for sharing care plans and requests.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

from supabase import Client
from app.db.repositories.care_request_repository import CareRequestRepository
from app.db.repositories.care_plan_repository import CarePlanRepository
from app.db.repositories.care_task_repository import CareTaskRepository
from app.middleware.auth import AuthUser

logger = logging.getLogger(__name__)


class ShareService:
    """Service for share link operations"""
    
    def __init__(self, db: Client):
        self.db = db
        self.request_repo = CareRequestRepository(db)
        self.plan_repo = CarePlanRepository(db)
        self.task_repo = CareTaskRepository(db)
    
    async def generate_share_link(
        self,
        plan_id: str,
        user: AuthUser
    ) -> Dict[str, Any]:
        """
        Generate a share link for a care plan
        
        Args:
            plan_id: Care plan ID
            user: Authenticated user
            
        Returns:
            dict: Share token and URL
            
        Raises:
            HTTPException: If user doesn't have permission
        """
        try:
            # Get the plan
            plan = self.plan_repo.get_by_id(plan_id)
            
            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Care plan not found"
                )
            
            # Only creator can generate share link
            if plan["created_by"] != user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the plan creator can generate a share link"
                )
            
            # Enable sharing on the care request
            request_id = plan["care_request_id"]
            share_token = self.request_repo.enable_sharing(request_id)
            
            logger.info(f"Generated share link for plan {plan_id}")
            
            return {
                "share_token": share_token,
                "share_url": f"/shared/{share_token}"
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating share link: {str(e)}")
            raise
    
    async def access_shared_plan(
        self,
        share_token: str,
        user: Optional[AuthUser] = None
    ) -> Dict[str, Any]:
        """
        Access a care plan via share token
        
        Args:
            share_token: Share token
            user: Optional authenticated user
            
        Returns:
            dict: Care request with plan and tasks
            
        Raises:
            HTTPException: If share token is invalid
        """
        try:
            # Get care request by share token
            request = self.request_repo.get_by_share_token(share_token)
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Shared plan not found or sharing has been disabled"
                )
            
            # Get associated plan
            plan = self.plan_repo.get_by_request(request["id"])
            
            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Plan not found for this request"
                )
            
            # Get tasks
            plan = self.plan_repo.get_with_tasks(plan["id"])
            if plan.get("tasks"):
                self.task_repo.enrich_tasks_with_claimer_name(plan["tasks"])
            
            # Combine request and plan data
            result = {
                "care_request": request,
                "care_plan": plan,
                "is_authenticated": user is not None
            }
            
            logger.info(f"Accessed shared plan via token {share_token}")
            return result
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error accessing shared plan: {str(e)}")
            raise
    
    async def disable_sharing(
        self,
        plan_id: str,
        user: AuthUser
    ) -> bool:
        """
        Disable sharing for a care plan
        
        Args:
            plan_id: Care plan ID
            user: Authenticated user
            
        Returns:
            bool: True if disabled successfully
            
        Raises:
            HTTPException: If user doesn't have permission
        """
        try:
            # Get the plan
            plan = self.plan_repo.get_by_id(plan_id)
            
            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Care plan not found"
                )
            
            # Only creator can disable sharing
            if plan["created_by"] != user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the plan creator can disable sharing"
                )
            
            # Disable sharing on the care request
            request_id = plan["care_request_id"]
            self.request_repo.disable_sharing(request_id)
            
            logger.info(f"Disabled sharing for plan {plan_id}")
            return True
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error disabling sharing: {str(e)}")
            raise
