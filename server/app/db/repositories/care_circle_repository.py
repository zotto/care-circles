"""
Care Circle Repository

Database operations for care circles and memberships.
"""

import logging
from typing import List, Dict, Any, Optional
from supabase import Client

from app.db.repositories.base import BaseRepository
from app.config.constants import CircleMemberRole

logger = logging.getLogger(__name__)


class CareCircleRepository(BaseRepository):
    """Repository for care circle operations"""
    
    def __init__(self, db: Client):
        super().__init__(db, "care_circles")
    
    def get_user_circles(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all care circles for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List[dict]: List of care circles
        """
        try:
            # Query circles through membership table
            result = self.db.table("care_circle_members").select(
                "care_circles(*)"
            ).eq("user_id", user_id).execute()
            
            # Extract circles from nested structure
            circles = [item["care_circles"] for item in result.data if item.get("care_circles")]
            return circles
        
        except Exception as e:
            logger.error(f"Error getting user circles: {str(e)}")
            raise
    
    def add_member(
        self,
        circle_id: str,
        user_id: str,
        role: str = CircleMemberRole.MEMBER
    ) -> Dict[str, Any]:
        """
        Add a member to a care circle
        
        Args:
            circle_id: Care circle ID
            user_id: User ID to add
            role: Member role (owner or member)
            
        Returns:
            dict: Membership record
        """
        try:
            data = {
                "care_circle_id": circle_id,
                "user_id": user_id,
                "role": role
            }
            
            result = self.db.table("care_circle_members").insert(data).execute()
            
            if not result.data:
                raise Exception("Failed to add circle member")
            
            logger.debug(f"Added user {user_id} to circle {circle_id}")
            return result.data[0]
        
        except Exception as e:
            logger.error(f"Error adding circle member: {str(e)}")
            raise
    
    def remove_member(self, circle_id: str, user_id: str) -> bool:
        """
        Remove a member from a care circle
        
        Args:
            circle_id: Care circle ID
            user_id: User ID to remove
            
        Returns:
            bool: True if removed successfully
        """
        try:
            self.db.table("care_circle_members").delete().eq(
                "care_circle_id", circle_id
            ).eq("user_id", user_id).execute()
            
            logger.debug(f"Removed user {user_id} from circle {circle_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error removing circle member: {str(e)}")
            raise
    
    def get_members(self, circle_id: str) -> List[Dict[str, Any]]:
        """
        Get all members of a care circle
        
        Args:
            circle_id: Care circle ID
            
        Returns:
            List[dict]: List of members with user info
        """
        try:
            result = self.db.table("care_circle_members").select(
                "*, users(*)"
            ).eq("care_circle_id", circle_id).execute()
            
            return result.data
        
        except Exception as e:
            logger.error(f"Error getting circle members: {str(e)}")
            raise
    
    def is_member(self, circle_id: str, user_id: str) -> bool:
        """
        Check if user is a member of circle
        
        Args:
            circle_id: Care circle ID
            user_id: User ID
            
        Returns:
            bool: True if user is a member
        """
        try:
            result = self.db.table("care_circle_members").select("id").eq(
                "care_circle_id", circle_id
            ).eq("user_id", user_id).execute()
            
            return len(result.data) > 0
        
        except Exception as e:
            logger.error(f"Error checking circle membership: {str(e)}")
            raise
