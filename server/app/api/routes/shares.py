"""
Share API routes

Handles share link generation and access.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.middleware.auth import get_current_user, get_optional_user, AuthUser
from app.db import get_service_client
from app.services.share_service import ShareService

logger = logging.getLogger(__name__)

router = APIRouter()


class ShareLinkResponse(BaseModel):
    """Response model for share link"""
    share_token: str
    share_url: str


@router.post(
    "/care-plans/{plan_id}/share",
    response_model=ShareLinkResponse,
    summary="Generate share link",
    description="Generate a share link for care plan (creator only)"
)
async def generate_share_link(
    plan_id: str,
    user: AuthUser = Depends(get_current_user)
):
    """
    Generate a share link for care plan (creator only)
    
    Args:
        plan_id: Care plan ID
        user: Authenticated user from JWT
        
    Returns:
        ShareLinkResponse: Share token and URL
    """
    try:
        db = get_service_client()
        share_service = ShareService(db)
        
        share_data = await share_service.generate_share_link(plan_id, user)
        
        return share_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating share link: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate share link"
        )


@router.delete(
    "/care-plans/{plan_id}/share",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Disable sharing",
    description="Disable sharing for care plan (creator only)"
)
async def disable_sharing(
    plan_id: str,
    user: AuthUser = Depends(get_current_user)
):
    """
    Disable sharing for care plan (creator only)
    
    Args:
        plan_id: Care plan ID
        user: Authenticated user from JWT
    """
    try:
        db = get_service_client()
        share_service = ShareService(db)
        
        await share_service.disable_sharing(plan_id, user)
        
        return
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling sharing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable sharing"
        )


@router.get(
    "/shares/{share_token}",
    response_model=dict,
    summary="Access shared plan",
    description="Access a care plan via share token (public or authenticated)"
)
async def access_shared_plan(
    share_token: str,
    user: AuthUser | None = Depends(get_optional_user)
):
    """
    Access a care plan via share token
    
    This endpoint can be accessed with or without authentication.
    Authenticated users can claim tasks from the plan.
    
    Args:
        share_token: Share token from URL
        user: Optional authenticated user from JWT
        
    Returns:
        dict: Care request with plan and tasks
    """
    try:
        db = get_service_client()
        share_service = ShareService(db)
        
        plan_data = await share_service.access_shared_plan(share_token, user)
        
        return plan_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accessing shared plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to access shared plan"
        )
