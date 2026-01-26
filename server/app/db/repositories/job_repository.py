"""
Job Repository

Database operations for background jobs.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from supabase import Client

from app.db.repositories.base import BaseRepository
from app.config.constants import JobStatus

logger = logging.getLogger(__name__)


class JobRepository(BaseRepository):
    """Repository for job operations"""
    
    def __init__(self, db: Client):
        super().__init__(db, "jobs")
    
    def get_by_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job by care request ID
        
        Args:
            request_id: Care request ID
            
        Returns:
            Optional[dict]: Job or None
        """
        try:
            result = self.db.table(self.table_name).select("*").eq(
                "care_request_id", request_id
            ).order("created_at", desc=True).limit(1).execute()
            
            if not result.data:
                return None
            
            return result.data[0]
        
        except Exception as e:
            logger.error(f"Error getting job by request: {str(e)}")
            raise
    
    def update_status(
        self,
        job_id: str,
        status: str,
        current_agent: Optional[str] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update job status
        
        Args:
            job_id: Job ID
            status: New status
            current_agent: Currently executing agent
            error: Error message if failed
            
        Returns:
            dict: Updated job
        """
        try:
            updates = {"status": status}
            
            if current_agent:
                updates["current_agent"] = current_agent
            
            if error:
                updates["error"] = error
            
            # Set timestamps based on status
            if status == JobStatus.RUNNING and not self.get_by_id(job_id).get("started_at"):
                updates["started_at"] = datetime.utcnow().isoformat()
            
            if status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                updates["completed_at"] = datetime.utcnow().isoformat()
            
            result = self.update(job_id, updates)
            
            if not result:
                raise Exception(f"Failed to update job {job_id}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error updating job status: {str(e)}")
            raise
    
    def update_agent_progress(
        self,
        job_id: str,
        agent_name: str,
        agent_status: str
    ) -> Dict[str, Any]:
        """
        Update agent progress in job
        
        Args:
            job_id: Job ID
            agent_name: Agent name
            agent_status: Agent status
            
        Returns:
            dict: Updated job
        """
        try:
            # Get current job
            job = self.get_by_id(job_id)
            
            if not job:
                raise Exception(f"Job {job_id} not found")
            
            # Update agent progress
            agent_progress = job.get("agent_progress", {})
            agent_progress[agent_name] = agent_status
            
            updates = {
                "agent_progress": agent_progress,
                "current_agent": agent_name
            }
            
            result = self.update(job_id, updates)
            
            if not result:
                raise Exception(f"Failed to update agent progress for job {job_id}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error updating agent progress: {str(e)}")
            raise
    
    def store_result(self, job_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store job result
        
        Args:
            job_id: Job ID
            result: Result data
            
        Returns:
            dict: Updated job
        """
        try:
            updates = {"result": result}
            updated_job = self.update(job_id, updates)
            
            if not updated_job:
                raise Exception(f"Failed to store result for job {job_id}")
            
            return updated_job
        
        except Exception as e:
            logger.error(f"Error storing job result: {str(e)}")
            raise
    
    def get_active_jobs(self) -> List[Dict[str, Any]]:
        """
        Get all active (queued or running) jobs
        
        Returns:
            List[dict]: List of active jobs
        """
        try:
            result = self.db.table(self.table_name).select("*").in_(
                "status", [JobStatus.QUEUED, JobStatus.RUNNING]
            ).order("created_at").execute()
            
            return result.data
        
        except Exception as e:
            logger.error(f"Error getting active jobs: {str(e)}")
            raise
