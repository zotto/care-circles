"""
Care Circles FastAPI Application

Main application entry point for the Care Circles AI-assisted coordination system.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.config.constants import APIConstants
from app.middleware.cors import setup_cors
from app.middleware.error_handlers import setup_error_handlers
from app.models.responses import HealthCheckResponse
from app.api.routes import care_requests, jobs, auth, users, care_plans, tasks, shares
from app.services.job_runner import JobRunner

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global job runner instance
job_runner: JobRunner = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    global job_runner
    logger.info("Starting Care Circles API server...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize job runner
    job_runner = JobRunner()
    logger.info("Job runner initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Care Circles API server...")


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Setup middleware
setup_cors(app)
setup_error_handlers(app)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(care_requests.router, prefix="/api", tags=["Care Requests"])
app.include_router(care_plans.router, prefix="/api", tags=["Care Plans"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(shares.router, prefix="/api", tags=["Shares"])
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns the current status and version of the API.
    """
    return HealthCheckResponse(
        status="healthy",
        version=settings.API_VERSION
    )


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information
    """
    return JSONResponse(
        content={
            "service": settings.API_TITLE,
            "version": settings.API_VERSION,
            "status": "running",
            "docs": "/docs" if settings.DEBUG else "disabled",
        }
    )


def get_job_runner() -> JobRunner:
    """
    Get the global job runner instance
    
    Returns:
        JobRunner: The global job runner instance
    """
    return job_runner
