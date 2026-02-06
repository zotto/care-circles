"""
Observability API endpoints

Provides endpoints for metrics, agent stats, evaluations, and raw export.
Observability dashboards are viewed via Opik (Comet) directly.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.observability.metrics import metrics_collector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/observability", tags=["observability"])


class MetricsSummaryResponse(BaseModel):
    """Response model for metrics summary"""
    summary: Dict[str, Any]
    pipeline_statistics: Dict[str, Any]
    agent_statistics: Dict[str, Any]
    evaluation_summary: Dict[str, Any]


@router.get("/metrics/summary", response_model=MetricsSummaryResponse)
async def get_metrics_summary():
    """
    Get summary of all collected metrics
    
    Returns aggregated statistics for:
    - Pipeline executions
    - Agent performance
    - Evaluation scores
    """
    try:
        report = metrics_collector.get_comprehensive_report()
        
        return MetricsSummaryResponse(
            summary=report.get("summary", {}),
            pipeline_statistics=report.get("pipeline_statistics", {}),
            agent_statistics=report.get("agent_statistics", {}),
            evaluation_summary=report.get("evaluation_summary", {})
        )
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/agent/{agent_name}")
async def get_agent_metrics(agent_name: str):
    """
    Get metrics for a specific agent
    
    Args:
        agent_name: Name of the agent (e.g., "A1_intake_analyst")
    """
    try:
        stats = metrics_collector.get_agent_statistics(agent_name)
        
        if not stats:
            raise HTTPException(
                status_code=404,
                detail=f"No metrics found for agent: {agent_name}"
            )
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/evaluations")
async def get_evaluation_metrics():
    """
    Get evaluation score summaries
    
    Returns aggregated evaluation scores across all runs
    """
    try:
        summary = metrics_collector.get_evaluation_summary()
        
        if not summary:
            return {
                "message": "No evaluation metrics available yet",
                "evaluations": {}
            }
        
        return summary
    except Exception as e:
        logger.error(f"Error getting evaluation metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/raw")
async def export_raw_metrics():
    """
    Export all raw metrics data
    
    Returns complete raw metrics for external analysis
    """
    try:
        raw_data = metrics_collector.export_to_dict()
        
        return {
            "message": "Raw metrics exported successfully",
            "data": raw_data
        }
    except Exception as e:
        logger.error(f"Error exporting raw metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metrics/reset")
async def reset_metrics():
    """
    Reset all collected metrics
    
    WARNING: This will clear all metrics data. Use with caution.
    """
    try:
        metrics_collector.reset()
        return {"message": "Metrics reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
