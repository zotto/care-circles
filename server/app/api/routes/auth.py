"""
Authentication API routes

Handles user authentication and profile management.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.middleware.auth import get_current_user, AuthUser
from app.db import get_service_client
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter()


class MagicLinkRequest(BaseModel):
    """Request model for magic link"""
    email: EmailStr


class MagicLinkResponse(BaseModel):
    """Response model for magic link"""
    message: str
    email: str


class UserProfileResponse(BaseModel):
    """User profile response"""
    id: str
    email: str
    full_name: str | None


class UserProfileUpdate(BaseModel):
    """User profile update request"""
    full_name: str | None = None


@router.post(
    "/auth/magic-link",
    response_model=MagicLinkResponse,
    summary="Request magic link",
    description="Send a magic link to user's email for passwordless authentication"
)
async def request_magic_link(request: MagicLinkRequest):
    """
    Request a magic link for authentication
    
    Supabase will send an email with a magic link. User clicks the link
    and is redirected to the app with authentication tokens.
    
    Args:
        request: Magic link request with email
        
    Returns:
        MagicLinkResponse: Confirmation message
    """
    try:
        db = get_service_client()
        
        # Request magic link from Supabase
        response = db.auth.sign_in_with_otp({
            "email": request.email,
            "options": {
                "should_create_user": True
            }
        })
        
        logger.info(f"Magic link sent to {request.email}")
        
        return MagicLinkResponse(
            message="Magic link sent! Check your email.",
            email=request.email
        )
    
    except Exception as e:
        logger.error(f"Error sending magic link: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send magic link"
        )


@router.get(
    "/auth/me",
    response_model=UserProfileResponse,
    summary="Get current user",
    description="Get authenticated user's profile"
)
async def get_current_user_profile(
    user: AuthUser = Depends(get_current_user)
):
    """
    Get current authenticated user's profile
    
    Args:
        user: Authenticated user from JWT
        
    Returns:
        UserProfileResponse: User profile
    """
    try:
        db = get_service_client()
        auth_service = AuthService(db)
        
        # Ensure user profile exists
        profile = await auth_service.validate_user_access(user)
        
        return UserProfileResponse(
            id=profile["id"],
            email=profile["email"],
            full_name=profile.get("full_name")
        )
    
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@router.patch(
    "/auth/me",
    response_model=UserProfileResponse,
    summary="Update current user",
    description="Update authenticated user's profile"
)
async def update_current_user_profile(
    updates: UserProfileUpdate,
    user: AuthUser = Depends(get_current_user)
):
    """
    Update current authenticated user's profile
    
    Args:
        updates: Profile updates
        user: Authenticated user from JWT
        
    Returns:
        UserProfileResponse: Updated user profile
    """
    try:
        db = get_service_client()
        auth_service = AuthService(db)
        
        # Update profile
        profile = await auth_service.update_user_profile(
            user.user_id,
            updates.model_dump(exclude_unset=True)
        )
        
        return UserProfileResponse(
            id=profile["id"],
            email=profile["email"],
            full_name=profile.get("full_name")
        )
    
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
