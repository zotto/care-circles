"""
Global error handlers for the API
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


def setup_error_handlers(app: FastAPI) -> None:
    """
    Configure global error handlers for the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors"""
        logger.warning(f"Validation error on {request.url}: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "detail": exc.errors(),
                "status_code": 422
            }
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """Handle Pydantic model validation errors"""
        logger.warning(f"Model validation error on {request.url}: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Model Validation Error",
                "detail": exc.errors(),
                "status_code": 422
            }
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError exceptions"""
        logger.warning(f"Value error on {request.url}: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Bad Request",
                "detail": str(exc),
                "status_code": 400
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        logger.error(f"Unhandled exception on {request.url}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred. Please try again later.",
                "status_code": 500
            }
        )
