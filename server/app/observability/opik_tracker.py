"""
Opik tracking decorators and utilities

Provides decorator-based tracking that integrates seamlessly with Opik dashboard.
"""

import logging
from typing import Any, Dict, Optional, Callable
from functools import wraps

try:
    import opik
    from opik import Opik
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    logging.warning("Opik not installed. Tracking decorators will be no-ops.")

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Global Opik client instance
_opik_client: Optional[Opik] = None


def configure_opik():
    """Configure Opik with settings and create client instance"""
    global _opik_client
    
    if OPIK_AVAILABLE and settings.OPIK_API_KEY:
        try:
            opik.configure(
                api_key=settings.OPIK_API_KEY,
                workspace=settings.OPIK_WORKSPACE
            )
            
            # Create the Opik client instance
            _opik_client = Opik(
                project_name=settings.OPIK_PROJECT_NAME,
                workspace=settings.OPIK_WORKSPACE
            )
            
            logger.info(f"Opik configured: workspace={settings.OPIK_WORKSPACE}, project={settings.OPIK_PROJECT_NAME}")
            return True
        except Exception as e:
            logger.error(f"Failed to configure Opik: {e}")
            return False
    return False


def log_to_opik(
    name: str,
    input_data: Any,
    output_data: Any,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Manually log a trace to Opik using the low-level client API
    
    Args:
        name: Name of the trace
        input_data: Input data
        output_data: Output data
        metadata: Additional metadata
    """
    if not OPIK_AVAILABLE or not settings.OPIK_API_KEY or _opik_client is None:
        return
    
    try:
        # Convert input/output to dict format
        input_dict = input_data if isinstance(input_data, dict) else {"data": str(input_data)}
        output_dict = output_data if isinstance(output_data, dict) else {"result": str(output_data)}
        
        # Create a trace using the low-level client
        trace = _opik_client.trace(
            name=name,
            input=input_dict,
            output=output_dict,
            metadata=metadata or {},
            tags=[name.split("_")[0]] if "_" in name else []
        )
        
        # End the trace to ensure it's sent
        trace.end()
        
        logger.info(f"Logged to Opik: {name}")
    except Exception as e:
        logger.error(f"Failed to log to Opik: {e}", exc_info=True)


# Initialize Opik on module load
_opik_configured = configure_opik()
