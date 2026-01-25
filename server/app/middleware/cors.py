"""
CORS middleware configuration
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.config.settings import settings


def setup_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware for the FastAPI application
    
    Allows requests from configured frontend origins.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
