"""
Development server launcher

Simple script to run the FastAPI server with uvicorn.
"""

import uvicorn
from app.config.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
