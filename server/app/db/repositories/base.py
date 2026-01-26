"""
Base Repository

Abstract base class providing common CRUD operations for all repositories.
"""

import logging
from typing import Generic, TypeVar, Optional, List, Dict, Any
from uuid import uuid4
from datetime import datetime
from supabase import Client

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base repository providing common database operations
    
    All specific repositories should inherit from this class and implement
    the abstract methods for their specific domain models.
    """
    
    def __init__(self, db: Client, table_name: str):
        """
        Initialize repository
        
        Args:
            db: Supabase client
            table_name: Name of the database table
        """
        self.db = db
        self.table_name = table_name
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record
        
        Args:
            data: Record data
            
        Returns:
            dict: Created record
            
        Raises:
            Exception: If creation fails
        """
        try:
            # Add ID if not provided
            if "id" not in data:
                data["id"] = str(uuid4())
            
            # Add timestamps if not provided
            if "created_at" not in data:
                data["created_at"] = datetime.utcnow().isoformat()
            
            result = self.db.table(self.table_name).insert(data).execute()
            
            if not result.data:
                raise Exception(f"Failed to create {self.table_name} record")
            
            logger.debug(f"Created {self.table_name} record: {result.data[0]['id']}")
            return result.data[0]
        
        except Exception as e:
            logger.error(f"Error creating {self.table_name}: {str(e)}")
            raise
    
    def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a record by ID
        
        Args:
            record_id: Record ID
            
        Returns:
            Optional[dict]: Record data or None if not found
        """
        try:
            result = self.db.table(self.table_name).select("*").eq(
                "id", record_id
            ).execute()
            
            if not result.data:
                return None
            
            return result.data[0]
        
        except Exception as e:
            logger.error(f"Error getting {self.table_name} by ID: {str(e)}")
            raise
    
    def list_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = "created_at",
        ascending: bool = False,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List all records with optional filtering
        
        Args:
            filters: Dictionary of column:value filters
            order_by: Column to order by
            ascending: Sort order (default descending)
            limit: Maximum number of records to return
            
        Returns:
            List[dict]: List of records
        """
        try:
            query = self.db.table(self.table_name).select("*")
            
            # Apply filters
            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)
            
            # Apply ordering
            query = query.order(order_by, desc=not ascending)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            result = query.execute()
            return result.data
        
        except Exception as e:
            logger.error(f"Error listing {self.table_name}: {str(e)}")
            raise
    
    def update(
        self,
        record_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a record
        
        Args:
            record_id: Record ID
            updates: Fields to update
            
        Returns:
            Optional[dict]: Updated record or None if not found
        """
        try:
            # Add updated_at timestamp
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            result = self.db.table(self.table_name).update(updates).eq(
                "id", record_id
            ).execute()
            
            if not result.data:
                return None
            
            logger.debug(f"Updated {self.table_name} record: {record_id}")
            return result.data[0]
        
        except Exception as e:
            logger.error(f"Error updating {self.table_name}: {str(e)}")
            raise
    
    def delete(self, record_id: str) -> bool:
        """
        Delete a record
        
        Args:
            record_id: Record ID
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            result = self.db.table(self.table_name).delete().eq(
                "id", record_id
            ).execute()
            
            logger.debug(f"Deleted {self.table_name} record: {record_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting {self.table_name}: {str(e)}")
            raise
    
    def exists(self, record_id: str) -> bool:
        """
        Check if a record exists
        
        Args:
            record_id: Record ID
            
        Returns:
            bool: True if record exists
        """
        try:
            result = self.db.table(self.table_name).select("id").eq(
                "id", record_id
            ).execute()
            
            return len(result.data) > 0
        
        except Exception as e:
            logger.error(f"Error checking {self.table_name} existence: {str(e)}")
            raise
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filtering
        
        Args:
            filters: Dictionary of column:value filters
            
        Returns:
            int: Number of records
        """
        try:
            query = self.db.table(self.table_name).select("id", count="exact")
            
            # Apply filters
            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)
            
            result = query.execute()
            return result.count if result.count is not None else 0
        
        except Exception as e:
            logger.error(f"Error counting {self.table_name}: {str(e)}")
            raise
