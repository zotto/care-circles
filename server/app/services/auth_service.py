"""
Authentication Service

Business logic for user authentication and token management.
"""

import logging
from typing import Optional, Dict, Any
from supabase import Client

from app.db.repositories.user_repository import UserRepository
from app.middleware.auth import AuthUser

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db: Client):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def get_or_create_user(
        self,
        user_id: str,
        email: str,
        full_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get or create user profile
        
        This is called after successful authentication to ensure
        the user profile exists in our database.
        
        Args:
            user_id: User ID from Supabase auth
            email: User email
            full_name: User full name (optional)
            
        Returns:
            dict: User profile
        """
        try:
            return self.user_repo.create_or_update(user_id, email, full_name)
        
        except Exception as e:
            logger.error(f"Error getting/creating user: {str(e)}")
            raise
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile by ID
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[dict]: User profile or None
        """
        try:
            return self.user_repo.get_by_id(user_id)
        
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise
    
    async def update_user_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update user profile
        
        Args:
            user_id: User ID
            updates: Fields to update
            
        Returns:
            Optional[dict]: Updated user profile
        """
        try:
            # Only allow updating certain fields
            allowed_fields = {"full_name"}
            filtered_updates = {
                k: v for k, v in updates.items() if k in allowed_fields
            }
            
            if not filtered_updates:
                return self.user_repo.get_by_id(user_id)
            
            return self.user_repo.update(user_id, filtered_updates)
        
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            raise
    
    async def validate_user_access(
        self,
        auth_user: AuthUser
    ) -> Dict[str, Any]:
        """
        Validate user has active profile and return it
        
        Args:
            auth_user: Authenticated user from JWT
            
        Returns:
            dict: User profile
            
        Raises:
            Exception: If user profile doesn't exist
        """
        profile = await self.get_user_profile(auth_user.user_id)
        
        if not profile:
            # Try to create profile from JWT data
            profile = await self.get_or_create_user(
                auth_user.user_id,
                auth_user.email
            )
        
        return profile
