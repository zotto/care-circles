"""
Care Circle Service

Business logic for care circle operations.
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4
from fastapi import HTTPException, status

from supabase import Client
from app.db.repositories.care_circle_repository import CareCircleRepository
from app.middleware.auth import AuthUser
from app.config.constants import CircleMemberRole

logger = logging.getLogger(__name__)


class CareCircleService:
    """Service for care circle operations"""
    
    def __init__(self, db: Client):
        self.db = db
        self.circle_repo = CareCircleRepository(db)
    
    async def create_circle(
        self,
        user: AuthUser,
        name: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Create a new care circle
        
        Args:
            user: Authenticated user (will be owner)
            name: Circle name
            description: Circle description
            
        Returns:
            dict: Created care circle
        """
        try:
            # Create circle
            circle_data = {
                "name": name,
                "description": description,
                "owner_id": user.user_id
            }
            
            circle = self.circle_repo.create(circle_data)
            
            # Add creator as owner member
            self.circle_repo.add_member(
                circle["id"],
                user.user_id,
                CircleMemberRole.OWNER
            )
            
            logger.info(f"Created care circle {circle['id']} for user {user.user_id}")
            return circle
        
        except Exception as e:
            logger.error(f"Error creating care circle: {str(e)}")
            raise
    
    async def get_circle(
        self,
        circle_id: str,
        user: AuthUser
    ) -> Dict[str, Any]:
        """
        Get care circle by ID
        
        Args:
            circle_id: Circle ID
            user: Authenticated user
            
        Returns:
            dict: Care circle with members
            
        Raises:
            HTTPException: If user doesn't have access
        """
        try:
            # Check if user is a member
            if not self.circle_repo.is_member(circle_id, user.user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this care circle"
                )
            
            circle = self.circle_repo.get_by_id(circle_id)
            
            if not circle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Care circle not found"
                )
            
            # Add members list
            members = self.circle_repo.get_members(circle_id)
            circle["members"] = members
            
            return circle
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting care circle: {str(e)}")
            raise
    
    async def list_user_circles(self, user: AuthUser) -> List[Dict[str, Any]]:
        """
        List all circles user is a member of
        
        Args:
            user: Authenticated user
            
        Returns:
            List[dict]: List of care circles
        """
        try:
            return self.circle_repo.get_user_circles(user.user_id)
        
        except Exception as e:
            logger.error(f"Error listing user circles: {str(e)}")
            raise
    
    async def update_circle(
        self,
        circle_id: str,
        user: AuthUser,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update care circle (owner only)
        
        Args:
            circle_id: Circle ID
            user: Authenticated user
            updates: Fields to update
            
        Returns:
            dict: Updated circle
            
        Raises:
            HTTPException: If user is not owner
        """
        try:
            # Check if user is owner
            circle = self.circle_repo.get_by_id(circle_id)
            
            if not circle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Care circle not found"
                )
            
            if circle["owner_id"] != user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the owner can update this care circle"
                )
            
            # Only allow updating certain fields
            allowed_fields = {"name", "description"}
            filtered_updates = {
                k: v for k, v in updates.items() if k in allowed_fields
            }
            
            return self.circle_repo.update(circle_id, filtered_updates)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating care circle: {str(e)}")
            raise
    
    async def add_member(
        self,
        circle_id: str,
        user_id: str,
        requesting_user: AuthUser
    ) -> Dict[str, Any]:
        """
        Add a member to care circle (owner only)
        
        Args:
            circle_id: Circle ID
            user_id: User ID to add
            requesting_user: User making the request
            
        Returns:
            dict: Membership record
            
        Raises:
            HTTPException: If requesting user is not owner
        """
        try:
            # Check if requesting user is owner
            circle = self.circle_repo.get_by_id(circle_id)
            
            if not circle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Care circle not found"
                )
            
            if circle["owner_id"] != requesting_user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the owner can add members"
                )
            
            # Add member
            return self.circle_repo.add_member(
                circle_id,
                user_id,
                CircleMemberRole.MEMBER
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding circle member: {str(e)}")
            raise
    
    async def remove_member(
        self,
        circle_id: str,
        user_id: str,
        requesting_user: AuthUser
    ) -> bool:
        """
        Remove a member from care circle (owner only)
        
        Args:
            circle_id: Circle ID
            user_id: User ID to remove
            requesting_user: User making the request
            
        Returns:
            bool: True if removed successfully
            
        Raises:
            HTTPException: If requesting user is not owner or trying to remove owner
        """
        try:
            # Check if requesting user is owner
            circle = self.circle_repo.get_by_id(circle_id)
            
            if not circle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Care circle not found"
                )
            
            if circle["owner_id"] != requesting_user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the owner can remove members"
                )
            
            # Can't remove the owner
            if user_id == circle["owner_id"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the circle owner"
                )
            
            return self.circle_repo.remove_member(circle_id, user_id)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error removing circle member: {str(e)}")
            raise
