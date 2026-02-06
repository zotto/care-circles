"""
Opik client for tracing and experiment tracking

Provides a centralized client for all Opik operations including:
- Tracing agent executions
- Logging experiments
- Recording metrics
- Managing evaluation runs
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import contextmanager

try:
    import opik
    from opik import track, opik_context
    from opik.api_objects import opik_client as opik_api_client
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    logging.warning("Opik not installed. Observability features will be disabled.")

from app.config.settings import settings

logger = logging.getLogger(__name__)


class OpikClient:
    """
    Centralized client for Opik observability and evaluation
    
    This client provides a unified interface for:
    - Tracing agent executions with detailed metadata
    - Creating and managing experiments
    - Recording custom metrics
    - Running evaluations on agent outputs
    """
    
    def __init__(self):
        """Initialize Opik client with configuration from settings"""
        self.enabled = OPIK_AVAILABLE and bool(settings.OPIK_API_KEY)
        self.current_experiment_id: Optional[str] = None
        
        if self.enabled:
            try:
                # Initialize Opik with configuration
                opik.configure(
                    api_key=settings.OPIK_API_KEY,
                    workspace=settings.OPIK_WORKSPACE
                )
                logger.info(
                    f"Opik configured successfully. "
                    f"Workspace: {settings.OPIK_WORKSPACE}, "
                    f"Project: {settings.OPIK_PROJECT_NAME}"
                )
            except Exception as e:
                logger.error(f"Failed to configure Opik: {e}", exc_info=True)
                self.enabled = False
        else:
            logger.warning("Opik observability is disabled (missing API key or package)")
    
    def is_enabled(self) -> bool:
        """Check if Opik observability is enabled"""
        return self.enabled
    
    @contextmanager
    def trace_agent(
        self,
        agent_name: str,
        task_name: str,
        input_data: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager for tracing an agent execution
        
        Args:
            agent_name: Name of the agent (e.g., "A1_intake_analyst")
            task_name: Name of the task being executed
            input_data: Input data for the agent
            metadata: Additional metadata to log
            
        Yields:
            Trace context for recording outputs and metrics
            
        Example:
            with opik_client.trace_agent("A1", "analyze_needs", input_text) as trace:
                result = agent.execute()
                trace.log_output(result)
                trace.log_metric("confidence", 0.95)
        """
        if not self.enabled:
            yield _DummyTrace()
            return
        
        try:
            # Use Opik's span tracking for proper dashboard integration
            span_name = f"{agent_name}_{task_name}"
            
            # Log the trace using Opik's logging API
            trace_data = {
                "name": span_name,
                "input": {"input_data": input_data[:1000]},  # Truncate for display
                "metadata": {
                    "agent_name": agent_name,
                    "task_name": task_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "project_name": settings.OPIK_PROJECT_NAME,
                    **(metadata or {})
                }
            }
            
            # Create trace context
            trace_ctx = _TraceContext(span_name, trace_data, self)
            
            yield trace_ctx
            
            # Finalize and log trace
            trace_ctx._finalize()
            
        except Exception as e:
            logger.error(f"Error in trace_agent: {e}", exc_info=True)
            yield _DummyTrace()
    
    def log_experiment(
        self,
        experiment_name: str,
        parameters: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Log an experiment with parameters and metadata
        
        Args:
            experiment_name: Name of the experiment
            parameters: Experiment parameters (e.g., model, temperature)
            metadata: Additional metadata
            
        Returns:
            Experiment ID if successful, None otherwise
        """
        if not self.enabled:
            return None
        
        try:
            # Log experiment using Opik's experiment tracking
            experiment_id = f"{experiment_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            self.current_experiment_id = experiment_id
            
            logger.info(f"Logged experiment: {experiment_name} (ID: {experiment_id})")
            return experiment_id
            
        except Exception as e:
            logger.error(f"Error logging experiment: {e}")
            return None
    
    def log_metrics(
        self,
        metrics: Dict[str, float],
        step: Optional[int] = None,
        context: Optional[str] = None
    ):
        """
        Log custom metrics
        
        Args:
            metrics: Dictionary of metric names to values
            step: Optional step number for time-series metrics
            context: Optional context (e.g., "A1_execution", "pipeline_complete")
        """
        if not self.enabled:
            return
        
        try:
            for metric_name, value in metrics.items():
                logger.info(f"Metric [{context}]: {metric_name} = {value}")
                # Metrics are typically logged as part of traces or experiments
                
        except Exception as e:
            logger.error(f"Error logging metrics: {e}")
    
    def create_dataset(
        self,
        name: str,
        items: List[Dict[str, Any]],
        description: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a dataset for evaluation
        
        Args:
            name: Dataset name
            items: List of dataset items (each with input/output/metadata)
            description: Optional dataset description
            
        Returns:
            Dataset ID if successful, None otherwise
        """
        if not self.enabled:
            return None
        
        try:
            # Create dataset using Opik's dataset API
            dataset = self.client.create_dataset(
                name=name,
                description=description or f"Dataset for {name}"
            )
            
            # Add items to dataset
            for item in items:
                dataset.insert(item)
            
            logger.info(f"Created dataset: {name} with {len(items)} items")
            return dataset.id
            
        except Exception as e:
            logger.error(f"Error creating dataset: {e}")
            return None


class _TraceContext:
    """Context object for an active trace"""
    
    def __init__(self, span_name: str, trace_data: Dict[str, Any], client: OpikClient):
        self.span_name = span_name
        self.trace_data = trace_data
        self.client = client
        self.start_time = datetime.utcnow()
        self.output_data = None
        self.error_data = None
        self.metrics = {}
    
    def log_output(self, output: Any, metadata: Optional[Dict[str, Any]] = None):
        """Log the output of the agent execution"""
        try:
            output_str = str(output)[:5000]  # Truncate for display
            self.output_data = {"result": output_str}
            if metadata:
                self.trace_data["metadata"].update(metadata)
        except Exception as e:
            logger.error(f"Error logging output: {e}")
    
    def log_metric(self, name: str, value: float):
        """Log a metric for this trace"""
        try:
            self.metrics[name] = value
            self.trace_data["metadata"][f"metric_{name}"] = value
        except Exception as e:
            logger.error(f"Error logging metric: {e}")
    
    def log_error(self, error: Exception):
        """Log an error that occurred during execution"""
        try:
            self.error_data = {"error": str(error)}
            self.trace_data["metadata"]["error_type"] = type(error).__name__
            self.trace_data["metadata"]["failed"] = True
        except Exception as e:
            logger.error(f"Error logging error: {e}")
    
    def end(self, success: bool = True):
        """Explicitly end the trace"""
        try:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
            self.trace_data["metadata"]["duration_seconds"] = duration
            self.trace_data["metadata"]["success"] = success
        except Exception as e:
            logger.error(f"Error ending trace: {e}")
    
    def _finalize(self):
        """Finalize and send trace to Opik"""
        try:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
            self.trace_data["metadata"]["duration_seconds"] = duration
            
            # Set output
            if self.error_data:
                self.trace_data["output"] = self.error_data
                self.trace_data["metadata"]["success"] = False
            elif self.output_data:
                self.trace_data["output"] = self.output_data
                self.trace_data["metadata"]["success"] = True
            
            # Log trace using Opik's track function
            opik.track(
                name=self.span_name,
                input=self.trace_data["input"],
                output=self.trace_data.get("output", {}),
                metadata=self.trace_data["metadata"],
                project_name=settings.OPIK_PROJECT_NAME
            )
            
            logger.info(f"Logged trace to Opik: {self.span_name}")
            
        except Exception as e:
            logger.error(f"Error finalizing trace: {e}", exc_info=True)


class _DummyTrace:
    """Dummy trace context when Opik is disabled"""
    
    def log_output(self, output: Any, metadata: Optional[Dict[str, Any]] = None):
        pass
    
    def log_metric(self, name: str, value: float):
        pass
    
    def log_error(self, error: Exception):
        pass
    
    def end(self, success: bool = True):
        pass


# Global client instance
opik_client = OpikClient()
