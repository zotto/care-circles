"""
Domain models for Care Circles API

These Pydantic models define the core domain entities and provide
validation, serialization, and documentation for the API.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from app.config.constants import (
    RequestStatus,
    JobStatus,
    TaskPriority,
    TaskStatus,
    ApprovalStatus,
    APIConstants
)


class CareCircle(BaseModel):
    """
    Represents a coordination group for caregiving
    """
    id: str = Field(..., description="Unique identifier for the care circle")
    name: str = Field(..., description="Name of the care circle")
    description: str = Field(..., description="Description of the care circle")
    created_by: str = Field(..., description="User ID of the creator")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class CareRequest(BaseModel):
    """
    Represents the initial caregiving narrative submitted by an organizer
    """
    id: str = Field(..., description="Unique identifier for the care request")
    care_circle_id: str = Field(..., description="Associated care circle ID")
    narrative: str = Field(..., description="The caregiving situation narrative")
    constraints: Optional[str] = Field(None, description="Timing and scheduling constraints")
    boundaries: Optional[str] = Field(None, description="Privacy concerns and boundaries")
    status: str = Field(default=RequestStatus.SUBMITTED, description="Current status of the request")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    @field_validator('narrative')
    @classmethod
    def validate_narrative(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Narrative cannot be empty")
        if len(v) > APIConstants.MAX_NARRATIVE_LENGTH:
            raise ValueError(f"Narrative exceeds maximum length of {APIConstants.MAX_NARRATIVE_LENGTH}")
        return v.strip()
    
    @field_validator('constraints')
    @classmethod
    def validate_constraints(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > APIConstants.MAX_CONSTRAINTS_LENGTH:
            raise ValueError(f"Constraints exceed maximum length of {APIConstants.MAX_CONSTRAINTS_LENGTH}")
        return v.strip() if v else None
    
    @field_validator('boundaries')
    @classmethod
    def validate_boundaries(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > APIConstants.MAX_BOUNDARIES_LENGTH:
            raise ValueError(f"Boundaries exceed maximum length of {APIConstants.MAX_BOUNDARIES_LENGTH}")
        return v.strip() if v else None


class NeedsMap(BaseModel):
    """
    Structured interpretation of a CareRequest produced by A1 agent
    """
    id: str = Field(..., description="Unique identifier for the needs map")
    care_request_id: str = Field(..., description="Associated care request ID")
    summary: str = Field(..., description="High-level summary of the situation")
    identified_needs: Dict[str, Any] = Field(..., description="Structured needs identified from narrative")
    risks: Dict[str, Any] = Field(..., description="Potential risks or concerns")
    assumptions: str = Field(..., description="Assumptions made during analysis")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class CareTask(BaseModel):
    """
    Actionable unit of work for helpers
    """
    id: str = Field(..., description="Unique identifier for the task")
    care_circle_id: str = Field(..., description="Associated care circle ID")
    care_request_id: str = Field(..., description="Associated care request ID")
    title: str = Field(..., description="Short, clear task title")
    description: str = Field(..., description="Detailed task description")
    category: str = Field(..., description="Task category (e.g., meals, transportation, medical)")
    priority: str = Field(default=TaskPriority.MEDIUM, description="Task priority level")
    status: str = Field(default=TaskStatus.DRAFT, description="Current task status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        valid_priorities = [TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH]
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")
        return v


class ReviewPacket(BaseModel):
    """
    Human approval artifact containing the generated care plan
    """
    id: str = Field(..., description="Unique identifier for the review packet")
    care_request_id: str = Field(..., description="Associated care request ID")
    summary: str = Field(..., description="Executive summary of the care plan")
    draft_tasks: List[CareTask] = Field(..., description="Generated tasks awaiting approval")
    agent_notes: str = Field(..., description="Notes and rationale from the agent pipeline")
    approval_status: str = Field(default=ApprovalStatus.PENDING, description="Approval status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class Job(BaseModel):
    """
    Tracks background execution of the agent pipeline
    """
    id: str = Field(..., description="Unique identifier for the job")
    care_request_id: str = Field(..., description="Associated care request ID")
    care_request: Optional[CareRequest] = Field(None, description="Associated care request object (for internal use)")
    status: str = Field(default=JobStatus.QUEUED, description="Current job status")
    current_agent: Optional[str] = Field(None, description="Currently executing agent (A1-A5)")
    agent_progress: Dict[str, str] = Field(default_factory=dict, description="Progress of each agent step")
    started_at: Optional[datetime] = Field(None, description="Job start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")
    error: Optional[str] = Field(None, description="Error message if job failed")
    result: Optional[Dict[str, Any]] = Field(None, description="Job result data")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = [JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.COMPLETED, JobStatus.FAILED]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return v
