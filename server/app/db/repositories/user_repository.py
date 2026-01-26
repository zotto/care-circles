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
        Create or update user profile
        
        Args:
            user_id: User ID from auth.users
            email: User email
            full_name: User full name (optional)
            
        Returns:
            dict: User record
        """
        try:
            # Check if user exists
            existing = self.get_by_id(user_id)
            
            if existing:
                # Update existing user
                updates = {"email": email}
                if full_name:
                    updates["full_name"] = full_name
                return self.update(user_id, updates)
            else:
                # Create new user
                data = {
                    "id": user_id,
                    "email": email,
                    "full_name": full_name
                }
                return self.create(data)
        
        except Exception as e:
            logger.error(f"Error creating/updating user: {str(e)}")
            raise
