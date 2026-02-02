"""
Permission Checking Utilities

Helper functions for checking user permissions on resources.
"""

import logging
from fastapi import HTTPException, status
from supabase import Client

from app.middleware.auth import AuthUser

logger = logging.getLogger(__name__)


class PermissionError(HTTPException):
    """Custom exception for permission errors"""

    def __init__(self, detail: str = "You don't have permission to access this resource"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


async def check_plan_access(db: Client, user: AuthUser, plan_id: str) -> bool:
    """
    Check if user has access to the specified care plan (plan creator or care request creator).
    """
    try:
        plan_result = db.table("care_plans").select("created_by, care_request_id").eq(
            "id", plan_id
        ).execute()
        if not plan_result.data:
            return False
        plan = plan_result.data[0]
        if plan["created_by"] == user.user_id:
            return True
        req_result = db.table("care_requests").select("created_by").eq(
            "id", plan["care_request_id"]
        ).execute()
        if not req_result.data:
            return False
        return req_result.data[0]["created_by"] == user.user_id
    except Exception as e:
        logger.error(f"Error checking plan access: {str(e)}")
        return False


async def require_plan_access(db: Client, user: AuthUser, plan_id: str) -> None:
    """Require user to have access to the specified plan."""
    has_access = await check_plan_access(db, user, plan_id)
    if not has_access:
        raise PermissionError("You don't have access to this care plan")
