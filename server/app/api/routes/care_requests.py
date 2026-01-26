"""
Care Requests API routes

Handles creation and retrieval of care requests.
"""

import logging
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.domain import CareRequest
from app.models.responses import CareRequestResponse, CareRequestCreate
from app.middleware.auth import get_current_user, AuthUser
from app.config.constants import RequestStatus
from app.db import get_service_client
from app.db.repositories.care_request_repository import CareRequestRepository
from app.db.repositories.job_repository import JobRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/care-requests",
    response_model=CareRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new care request",
    description="Submit a caregiving narrative to be processed by AI agents"
)
async def create_care_request(
    request: CareRequestCreate,
    user: AuthUser = Depends(get_current_user)
):
    """
    Create a new care request and enqueue it for AI agent processing.
    
    The request will be validated and immediately queued for processing
    by the agent pipeline (A1-A5). Returns the created care request
    and the associated job ID for status tracking.
    
    Args:
        request: The care request data
        user: Authenticated user from JWT
        
    Returns:
        CareRequestResponse: The created care request and job ID
    """
    from app.main import get_job_runner
    
    try:
        # Log incoming request for debugging
        logger.info(f"Received care request: care_circle_id={request.care_circle_id}, narrative_length={len(request.narrative) if request.narrative else 0}")
        
        db = get_service_client()
        request_repo = CareRequestRepository(db)
        
        # If no care_circle_id provided, create a default one for the user
        care_circle_id = request.care_circle_id
        if not care_circle_id:
            logger.info(f"No care_circle_id provided, creating default circle for user {user.user_id}")
            from app.db.repositories.care_circle_repository import CareCircleRepository
            circle_repo = CareCircleRepository(db)
            
            # Check if user already has a default circle
            user_circles = circle_repo.get_user_circles(user.user_id)
            if user_circles and len(user_circles) > 0:
                # Use the first circle
                care_circle_id = user_circles[0]["id"]
                logger.info(f"Using existing circle {care_circle_id} for user {user.user_id}")
            else:
                # Create a new default circle
                circle_data = {
                    "name": "My Care Circle",
                    "description": "Default care circle",
                    "owner_id": user.user_id
                }
                new_circle = circle_repo.create(circle_data)
                care_circle_id = new_circle["id"]
                logger.info(f"Created new default circle {care_circle_id} for user {user.user_id}")
                
                # Add user as owner member
                circle_repo.add_member(care_circle_id, user.user_id, "owner")
        
        # Create care request in database
        care_request_data = {
            "care_circle_id": care_circle_id,
            "created_by": user.user_id,
            "narrative": request.narrative,
            "constraints": request.constraints,
            "boundaries": request.boundaries,
            "status": RequestStatus.SUBMITTED
        }
        
        care_request_record = request_repo.create(care_request_data)
        
        # Create CareRequest domain object for job runner
        care_request = CareRequest(
            id=care_request_record["id"],
            care_circle_id=care_request_record["care_circle_id"],
            narrative=care_request_record["narrative"],
            constraints=care_request_record.get("constraints"),
            boundaries=care_request_record.get("boundaries"),
            status=care_request_record["status"],
            created_at=datetime.fromisoformat(care_request_record["created_at"])
        )
        
        logger.info(f"Created care request: {care_request.id}")
        
        # Enqueue job for agent processing
        runner = get_job_runner()
        job = await runner.enqueue_job(care_request)
        
        logger.info(f"Enqueued job {job.id} for care request {care_request.id}")
        
        # Update request status to processing in database
        request_repo.update(care_request.id, {"status": RequestStatus.PROCESSING})
        care_request.status = RequestStatus.PROCESSING
        
        return CareRequestResponse(
            care_request=care_request,
            job_id=job.id
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error creating care request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating care request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create care request. Please try again."
        )


@router.get(
    "/care-requests/{request_id}",
    response_model=CareRequest,
    summary="Get a care request by ID",
    description="Retrieve details of a specific care request"
)
async def get_care_request(
    request_id: str,
    user: AuthUser = Depends(get_current_user)
):
    """
    Retrieve a care request by its ID.
    
    Args:
        request_id: The care request ID
        user: Authenticated user from JWT
        
    Returns:
        CareRequest: The care request details
    """
    try:
        db = get_service_client()
        request_repo = CareRequestRepository(db)
        
        care_request_record = request_repo.get_by_id(request_id)
        
        if not care_request_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Care request {request_id} not found"
            )
        
        # Check if user has access (member of circle)
        from app.db.repositories.care_circle_repository import CareCircleRepository
        circle_repo = CareCircleRepository(db)
        
        if not circle_repo.is_member(care_request_record["care_circle_id"], user.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this care request"
            )
        
        # Convert to domain model
        return CareRequest(
            id=care_request_record["id"],
            care_circle_id=care_request_record["care_circle_id"],
            narrative=care_request_record["narrative"],
            constraints=care_request_record.get("constraints"),
            boundaries=care_request_record.get("boundaries"),
            status=care_request_record["status"],
            created_at=datetime.fromisoformat(care_request_record["created_at"])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting care request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get care request"
        )
