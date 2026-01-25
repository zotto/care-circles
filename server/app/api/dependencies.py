"""
Middleware module for API dependencies and auth placeholders
"""

from fastapi import Header, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)


async def auth_placeholder(authorization: Optional[str] = Header(None)) -> dict:
    """
    Auth placeholder dependency for future Supabase integration
    
    Currently logs the auth check and allows all requests.
    Will be replaced with proper JWT validation when Supabase auth is integrated.
    
    Args:
        authorization: Optional Authorization header
        
    Returns:
        dict: User context (placeholder)
    """
    logger.debug("Auth check - placeholder (allowing all requests)")  # Changed to DEBUG level
    
    # Placeholder user context
    return {
        "user_id": "placeholder_user",
        "role": "organizer"
    }


async def validate_request_size(content_length: Optional[int] = Header(None)) -> None:
    """
    Validate request size to prevent oversized payloads
    
    Args:
        content_length: Content-Length header value
        
    Raises:
        HTTPException: If request is too large
    """
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    
    if content_length and content_length > MAX_REQUEST_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Request too large. Maximum size is {MAX_REQUEST_SIZE} bytes"
        )
