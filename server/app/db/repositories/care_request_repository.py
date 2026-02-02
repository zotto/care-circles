"""
Care Request Repository

Database operations for care requests.
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4
from supabase import Client

from app.db.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class CareRequestRepository(BaseRepository):
    """Repository for care request operations"""
    
    def __init__(self, db: Client):
        super().__init__(db, "care_requests")
    
    def get_by_creator(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all care requests created by a user
        
        Args:
            user_id: User ID
            
        Returns:
            List[dict]: List of care requests
        """
        try:
            result = self.db.table(self.table_name).select("*").eq(
                "created_by", user_id
            ).order("created_at", desc=True).execute()
            
            return result.data
        
        except Exception as e:
            logger.error(f"Error getting requests by creator: {str(e)}")
            raise
    
    def get_by_share_token(self, share_token: str) -> Optional[Dict[str, Any]]:
        """
        Get care request by share token
        
        Args:
            share_token: Share token UUID
            
        Returns:
            Optional[dict]: Care request or None
        """
        try:
            result = self.db.table(self.table_name).select("*").eq(
                "share_token", share_token
            ).eq("is_shared", True).execute()
            
            if not result.data:
                return None
            
            return result.data[0]
        
        except Exception as e:
            logger.error(f"Error getting request by share token: {str(e)}")
            raise
    
    def enable_sharing(self, request_id: str) -> str:
        """
        Enable sharing for a care request and return share token
        
        Args:
            request_id: Care request ID
            
        Returns:
            str: Share token
        """
        try:
            # Get current request to check if it has a share token
            request = self.get_by_id(request_id)
            
            if not request:
                raise Exception(f"Care request {request_id} not found")
            
            share_token = request.get("share_token")
            
            # Generate new token if none exists
            if not share_token:
                share_token = str(uuid4())
            
            # Enable sharing
            self.update(request_id, {
                "is_shared": True,
                "share_token": share_token
            })
            
            logger.debug(f"Enabled sharing for request {request_id}")
            return share_token
        
        except Exception as e:
            logger.error(f"Error enabling sharing: {str(e)}")
            raise
    
    def disable_sharing(self, request_id: str) -> bool:
        """
        Disable sharing for a care request
        
        Args:
            request_id: Care request ID
            
        Returns:
            bool: True if disabled successfully
        """
        try:
            self.update(request_id, {"is_shared": False})
            logger.debug(f"Disabled sharing for request {request_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error disabling sharing: {str(e)}")
            raise
