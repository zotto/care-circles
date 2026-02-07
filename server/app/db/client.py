"""
Supabase Database Client

Provides database connectivity and client initialization for the Care Circles API.
"""

import logging
from typing import Optional
from supabase import create_client, Client

from app.config.settings import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Singleton Supabase client manager
    
    Provides both service-role (admin) and user-scoped clients for database operations.
    """
    
    _service_client: Optional[Client] = None
    _anon_client: Optional[Client] = None
    
    @classmethod
    def get_service_client(cls) -> Client:
        """
        Get Supabase service role client (bypasses RLS)
        
        Use this for:
        - Agent pipeline operations
        - System-level operations
        - Background job processing
        
        Returns:
            Client: Supabase client with service role key
        """
        if cls._service_client is None:
            logger.info("Initializing Supabase service role client")
            cls._service_client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY,
            )
            logger.info("Supabase service role client initialized")
        
        return cls._service_client
    
    @classmethod
    def get_anon_client(cls) -> Client:
        """
        Get Supabase anon client (respects RLS)
        
        Use this for:
        - Public operations
        - Initial auth operations
        
        Returns:
            Client: Supabase client with anon key
        """
        if cls._anon_client is None:
            logger.info("Initializing Supabase anon client")
            cls._anon_client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_ANON_KEY,
            )
            logger.info("Supabase anon client initialized")
        
        return cls._anon_client
    
    @classmethod
    def get_user_client(cls, access_token: str) -> Client:
        """
        Get user-scoped Supabase client (respects RLS for specific user)
        
        Use this for:
        - User-specific operations
        - Operations that should respect RLS
        
        Args:
            access_token: User's JWT access token
            
        Returns:
            Client: Supabase client scoped to user
        """
        client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_ANON_KEY,
        )
        # Set the auth token for this client
        client.auth.set_session(access_token, "")
        return client
    
    @classmethod
    def close_all(cls):
        """
        Close all client connections (for cleanup)
        """
        cls._service_client = None
        cls._anon_client = None
        logger.info("Closed all Supabase client connections")


# Convenience functions for getting clients
def get_service_client() -> Client:
    """Get service role client (bypasses RLS)"""
    return SupabaseClient.get_service_client()


def get_anon_client() -> Client:
    """Get anon client (respects RLS)"""
    return SupabaseClient.get_anon_client()


def get_user_client(access_token: str) -> Client:
    """Get user-scoped client (respects RLS for user)"""
    return SupabaseClient.get_user_client(access_token)
