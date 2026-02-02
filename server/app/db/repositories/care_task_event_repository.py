"""
Care Task Event Repository

Database operations for task diary events (status updates, completion outcomes, release reasons).
"""

import logging
from typing import List, Dict, Any

from supabase import Client

from app.db.repositories.base import BaseRepository
from app.config.constants import TaskEventType

logger = logging.getLogger(__name__)


class CareTaskEventRepository(BaseRepository):
    """Repository for care task event (diary) operations"""

    def __init__(self, db: Client):
        super().__init__(db, "care_task_events")

    def create_event(
        self,
        care_task_id: str,
        event_type: str,
        content: str,
        created_by: str,
    ) -> Dict[str, Any]:
        """
        Create a task diary event.

        Args:
            care_task_id: Task ID
            event_type: One of TaskEventType.STATUS_UPDATE, COMPLETED, RELEASED
            content: Event content (status note, outcome, or reason)
            created_by: User ID who created the event

        Returns:
            dict: Created event
        """
        data = {
            "care_task_id": care_task_id,
            "event_type": event_type,
            "content": content.strip(),
            "created_by": created_by,
        }
        return self.create(data)

    def get_by_task(self, care_task_id: str) -> List[Dict[str, Any]]:
        """
        Get all events for a task, ordered by created_at ascending (oldest first).

        Args:
            care_task_id: Task ID

        Returns:
            List[dict]: Events for the task
        """
        try:
            result = (
                self.db.table(self.table_name)
                .select("*")
                .eq("care_task_id", care_task_id)
                .order("created_at", desc=False)
                .execute()
            )
            return result.data
        except Exception as e:
            logger.error(f"Error getting events for task {care_task_id}: {str(e)}")
            raise
