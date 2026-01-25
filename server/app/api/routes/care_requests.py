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
from app.api.dependencies import auth_placeholder
from app.config.constants import RequestStatus

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
    user_context: dict = Depends(auth_placeholder)
):
    """
    Create a new care request and enqueue it for AI agent processing.
    
    The request will be validated and immediately queued for processing
    by the agent pipeline (A1-A5). Returns the created care request
    and the associated job ID for status tracking.
    
    Args:
        request: The care request data
        user_context: User authentication context (placeholder)
        
    Returns:
        CareRequestResponse: The created care request and job ID
    """
    from app.main import get_job_runner
    
    try:
        # Generate unique IDs
        care_request_id = f"req_{uuid4().hex[:16]}"
        care_circle_id = request.care_circle_id or f"circle_{uuid4().hex[:16]}"
        
        # Create CareRequest domain object
        care_request = CareRequest(
            id=care_request_id,
            care_circle_id=care_circle_id,
            narrative=request.narrative,
            constraints=request.constraints,
            boundaries=request.boundaries,
            status=RequestStatus.SUBMITTED,
            created_at=datetime.utcnow()
        )
        
        logger.info(f"Created care request: {care_request_id}")
        
        # Enqueue job for agent processing
        runner = get_job_runner()
        job = await runner.enqueue_job(care_request)
        
        logger.info(f"Enqueued job {job.id} for care request {care_request_id}")
        
        # Update request status to processing
        care_request.status = RequestStatus.PROCESSING
        
        return CareRequestResponse(
            care_request=care_request,
            job_id=job.id
        )
        
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
    user_context: dict = Depends(auth_placeholder)
):
    """
    Retrieve a care request by its ID.
    
    Note: In the current in-memory implementation, this endpoint will
    need to be enhanced when database persistence is added.
    
    Args:
        request_id: The care request ID
        user_context: User authentication context (placeholder)
        
    Returns:
        CareRequest: The care request details
    """
    from app.main import get_job_runner
    
    runner = get_job_runner()
    
    # Find the care request through jobs
    for job in runner.jobs.values():
        if job.care_request and job.care_request.id == request_id:
            return job.care_request
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Care request {request_id} not found"
    )
