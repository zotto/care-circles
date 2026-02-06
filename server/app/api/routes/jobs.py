"""
Jobs API routes

Handles job status queries and monitoring.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.responses import JobResponse, JobStatusResponse
from app.models.domain import CareTask
from app.api.dependencies import auth_placeholder

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="Get job status",
    description="Retrieve the current status of a background job. Returns immediately with current status. When completed, includes the list of generated tasks."
)
async def get_job_status(
    job_id: str,
    user_context: dict = Depends(auth_placeholder)
):
    """
    Get the status of a background job.
    
    Jobs represent the execution of the AI agent pipeline for a care request.
    Clients can poll this endpoint to track progress and retrieve results
    when the job completes.
    
    This endpoint returns immediately with the current job status:
    - queued: Job is waiting to be processed
    - running: Job is currently being processed (agents are executing)
    - completed: Job finished successfully (includes tasks in response)
    - failed: Job encountered an error (includes error message)
    
    Args:
        job_id: The job ID to query
        user_context: User authentication context (placeholder)
        
    Returns:
        JobStatusResponse: Cleaned job status with tasks when completed
    """
    from app.main import get_job_runner
    
    runner = get_job_runner()
    
    # Retrieve job from in-memory store
    job = runner.jobs.get(job_id)
    
    if not job:
        logger.warning(f"Job not found: {job_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    # Extract tasks and plan metadata from result if job is completed
    tasks = None
    summary = None
    suggested_plan_name = None
    if job.status == "completed" and job.result:
        if "tasks" in job.result:
            tasks = [CareTask(**task_dict) for task_dict in job.result["tasks"]]
        summary = job.result.get("summary")
        suggested_plan_name = job.result.get("suggested_plan_name")
    
    return JobStatusResponse(
        status=job.status,
        job_id=job.id,
        care_request_id=job.care_request_id,
        current_agent=job.current_agent,
        agent_progress=job.agent_progress,
        tasks=tasks,
        summary=summary,
        suggested_plan_name=suggested_plan_name,
        error=job.error,
        started_at=job.started_at,
        completed_at=job.completed_at
    )


@router.get(
    "/jobs",
    summary="List all jobs",
    description="Retrieve a list of all jobs (for debugging)"
)
async def list_jobs(
    user_context: dict = Depends(auth_placeholder)
):
    """
    List all jobs in the system.
    
    This endpoint is primarily for debugging and monitoring purposes.
    
    Args:
        user_context: User authentication context (placeholder)
        
    Returns:
        dict: List of all jobs with their statuses
    """
    from app.main import get_job_runner
    
    runner = get_job_runner()
    
    jobs_summary = []
    for job_id, job in runner.jobs.items():
        jobs_summary.append({
            "job_id": job_id,
            "status": job.status,
            "care_request_id": job.care_request_id,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "error": job.error
        })
    
    return {
        "total": len(jobs_summary),
        "jobs": jobs_summary
    }
