"""
API request and response models

These models define the shapes of data sent to and received from the API endpoints.
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from app.models.domain import CareRequest, Job, CareTask


# Request Models

class CareRequestCreate(BaseModel):
    """
    Request model for creating a new care request
    """
    narrative: str = Field(..., description="The caregiving situation narrative")
    constraints: Optional[str] = Field(None, description="Timing and scheduling constraints")
    boundaries: Optional[str] = Field(None, description="Privacy concerns and boundaries")


# Response Models

class CareRequestResponse(BaseModel):
    """
    Response model for care request operations
    """
    care_request: CareRequest
    job_id: str = Field(..., description="ID of the background job processing this request")


class JobResponse(BaseModel):
    """
    Response model for job status queries
    """
    job: Job
    care_request: Optional[CareRequest] = None


class JobStatusResponse(BaseModel):
    """
    Cleaned response model for job status queries (frontend-friendly)
    Returns only status and tasks when completed
    """
    status: str = Field(..., description="Current job status: queued, running, completed, failed")
    job_id: str = Field(..., description="Job identifier")
    care_request_id: str = Field(..., description="Associated care request ID")
    current_agent: Optional[str] = Field(None, description="Currently executing agent (A1-A5)")
    agent_progress: Dict[str, str] = Field(default_factory=dict, description="Progress of each agent step")
    tasks: Optional[List[CareTask]] = Field(None, description="Generated tasks (only when status is completed)")
    error: Optional[str] = Field(None, description="Error message (only when status is failed)")
    started_at: Optional[datetime] = Field(None, description="Job start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")


class ReviewPacketResponse(BaseModel):
    """
    Response model for review packet retrieval
    """
    id: str
    care_request_id: str
    summary: str
    draft_tasks: List[CareTask]
    agent_notes: str
    approval_status: str
    created_at: datetime


class HealthCheckResponse(BaseModel):
    """
    Response model for health check endpoint
    """
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Current timestamp")


class ErrorResponse(BaseModel):
    """
    Standard error response model
    """
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    status_code: int = Field(..., description="HTTP status code")
