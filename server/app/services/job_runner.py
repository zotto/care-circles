"""
Background job runner service

Manages asynchronous execution of the AI agent pipeline.
Uses in-memory storage for job tracking (will be replaced with database persistence).
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor

from app.models.domain import CareRequest, Job, ReviewPacket
from app.config.constants import JobStatus, RequestStatus

logger = logging.getLogger(__name__)

# Thread pool for running blocking crew operations
executor = ThreadPoolExecutor(max_workers=4)


class JobRunner:
    """
    Manages background execution of care request processing jobs.
    
    Jobs are tracked in-memory and executed asynchronously. Each job
    represents the execution of the full AI agent pipeline (A1-A5).
    """
    
    def __init__(self):
        """Initialize the job runner with empty job storage"""
        self.jobs: Dict[str, Job] = {}
        self._orchestrator = None
        logger.info("JobRunner initialized")
    
    @property
    def orchestrator(self):
        """Lazy-load the orchestrator to avoid circular imports"""
        if self._orchestrator is None:
            from app.observability.instrumented_orchestrator import InstrumentedOrchestrator
            self._orchestrator = InstrumentedOrchestrator()
            logger.info("Using InstrumentedOrchestrator with Opik observability")
        return self._orchestrator
    
    async def enqueue_job(self, care_request: CareRequest) -> Job:
        """
        Create and enqueue a new job for processing a care request.
        
        The job is immediately added to the in-memory store and execution
        is triggered asynchronously in the background.
        
        Args:
            care_request: The care request to process
            
        Returns:
            Job: The created job object
        """
        # Generate unique job ID
        job_id = f"job_{uuid4().hex[:16]}"
        
        # Create job object
        job = Job(
            id=job_id,
            care_request_id=care_request.id,
            care_request=care_request,
            status=JobStatus.QUEUED,
            current_agent=None,
            agent_progress={},
            started_at=None,
            completed_at=None,
            error=None
        )
        
        # Add to job store
        self.jobs[job_id] = job
        
        logger.info(f"Job {job_id} enqueued for care request {care_request.id}")
        
        # Trigger background execution (fire and forget)
        asyncio.create_task(self._execute_job(job_id))
        
        return job
    
    async def _execute_job(self, job_id: str) -> None:
        """
        Execute a job by running the agent pipeline.
        
        This method updates job status, handles errors, and stores results.
        Execution happens asynchronously in the background.
        
        Args:
            job_id: The ID of the job to execute
        """
        job = self.jobs.get(job_id)
        
        if not job:
            logger.error(f"Job {job_id} not found in store")
            return
        
        try:
            # Update status to running
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            logger.info(f"Job {job_id} execution started")
            
            # Get care request
            care_request = job.care_request
            if not care_request:
                raise ValueError(f"No care request found for job {job_id}")
            
            # Execute the agent pipeline with progress tracking
            logger.info(f"Running agent pipeline for job {job_id}")
            
            # Define progress callback
            def update_progress(agent_name: str, status: str):
                job.current_agent = agent_name
                job.agent_progress[agent_name] = status
                logger.info(f"Job {job_id}: {agent_name} - {status}")
            
            # Run the pipeline in a thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            review_packet = await loop.run_in_executor(
                executor,
                self.orchestrator.run_pipeline_sync,
                care_request,
                update_progress
            )
            
            # Store result with tasks for easy access
            job.result = {
                "review_packet_id": review_packet.id,
                "summary": review_packet.summary,
                "task_count": len(review_packet.draft_tasks),
                "tasks": [task.model_dump() for task in review_packet.draft_tasks],
                "agent_notes": review_packet.agent_notes
            }
            
            # Also store the full review_packet for reference
            setattr(job, '_review_packet', review_packet)
            
            # Update status to completed
            job.status = JobStatus.COMPLETED
            job.current_agent = None
            job.completed_at = datetime.utcnow()
            
            # Update care request status
            if care_request:
                care_request.status = RequestStatus.COMPLETED
            
            logger.info(f"Job {job_id} completed successfully")
            logger.info(f"Generated {len(review_packet.draft_tasks)} tasks")
            
        except Exception as e:
            # Handle execution errors
            error_msg = f"Job execution failed: {str(e)}"
            logger.error(f"Job {job_id} failed: {error_msg}", exc_info=True)
            
            job.status = JobStatus.FAILED
            job.error = error_msg
            job.current_agent = None
            job.completed_at = datetime.utcnow()
            
            # Update care request status
            if job.care_request:
                job.care_request.status = RequestStatus.SUBMITTED  # Reset to submitted on failure
    
    def get_job(self, job_id: str) -> Job:
        """
        Retrieve a job by ID.
        
        Args:
            job_id: The job ID to retrieve
            
        Returns:
            Job: The job object, or None if not found
        """
        return self.jobs.get(job_id)
    
    def get_all_jobs(self) -> Dict[str, Job]:
        """
        Get all jobs in the store.
        
        Returns:
            Dict[str, Job]: Dictionary of all jobs
        """
        return self.jobs
