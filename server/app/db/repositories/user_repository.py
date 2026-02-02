"""
User Repository

Database operations for user profiles.
"""

import logging
from typing import Optional, Dict, Any
from supabase import Client

from app.db.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    """Repository for user operations"""
    
    def __init__(self, db: Client):
        super().__init__(db, "users")
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            Optional[dict]: User record or None
        """
        try:
            result = self.db.table(self.table_name).select("*").eq(
                "email", email
            ).execute()
            
            if not result.data:
                return None
            
            return result.data[0]
        
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise
    
    def create_or_update(
        self,
        user_id: str,
        email: str,
        full_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create or update user profile.
        Only PATCHes when email or full_name actually changed to avoid redundant updates.
        """
        try:
            existing = self.get_by_id(user_id)

            if existing:
                updates: Dict[str, Any] = {}
                if existing.get("email") != email:
                    updates["email"] = email
                if full_name is not None and existing.get("full_name") != full_name:
                    updates["full_name"] = full_name
                if updates:
                    return self.update(user_id, updates)
                return existing
            else:
                data = {
                    "id": user_id,
                    "email": email,
                    "full_name": full_name
                }
                return self.create(data)

        except Exception as e:
            logger.error(f"Error creating/updating user: {str(e)}")
            raise
