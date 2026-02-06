"""
Observability and evaluation module for Care Circles

This module provides comprehensive observability and evaluation capabilities
using Comet Opik for the AI agent pipeline.
"""

from app.observability.opik_client import OpikClient
from app.observability.evaluators import (
    TaskQualityEvaluator,
    BoundaryComplianceEvaluator,
    CompletenessEvaluator,
    ClarityEvaluator,
    PipelinePerformanceEvaluator
)
from app.observability.metrics import MetricsCollector

__all__ = [
    "OpikClient",
    "TaskQualityEvaluator",
    "BoundaryComplianceEvaluator",
    "CompletenessEvaluator",
    "ClarityEvaluator",
    "PipelinePerformanceEvaluator",
    "MetricsCollector"
]
