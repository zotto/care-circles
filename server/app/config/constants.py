"""
Application constants for Care Circles API

This module contains all constant values used throughout the application.
Using classes for constants provides clear namespacing and avoids magic numbers.
"""


class APIConstants:
    """API configuration constants"""
    
    DEFAULT_PORT = 8000
    MAX_NARRATIVE_LENGTH = 5000
    MAX_CONSTRAINTS_LENGTH = 2000
    MAX_BOUNDARIES_LENGTH = 2000
    REQUEST_TIMEOUT_SECONDS = 300
    JOB_POLL_INTERVAL_SECONDS = 2
    MAX_RETRIES = 3


class JobStatus:
    """Job status constants"""
    
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RequestStatus:
    """Care request status constants"""
    
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    COMPLETED = "completed"


class TaskPriority:
    """Task priority levels"""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus:
    """Care task status constants"""
    
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"


class ApprovalStatus:
    """Review packet approval status"""
    
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AgentNames:
    """CrewAI agent identifiers"""
    
    INTAKE_ANALYST = "intake_analyst"
    TASK_GENERATOR = "task_generator"
    GUARDIAN_REVIEWER = "guardian_reviewer"
    OPTIMIZATION_SPECIALIST = "optimization_specialist"
    REVIEW_ASSEMBLER = "review_assembler"


class TaskNames:
    """CrewAI task identifiers"""
    
    ANALYZE_NEEDS = "analyze_needs"
    GENERATE_TASKS = "generate_tasks"
    REVIEW_QUALITY = "review_quality"
    OPTIMIZE_PLAN = "optimize_plan"
    ASSEMBLE_REVIEW = "assemble_review"
