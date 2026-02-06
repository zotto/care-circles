"""
Metrics collection and aggregation for Care Circles

Provides utilities for collecting, aggregating, and reporting metrics
from agent executions and evaluations.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    """Metrics for a single agent execution"""
    agent_name: str
    task_name: str
    duration_seconds: float
    success: bool
    input_length: int
    output_length: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    custom_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class PipelineMetrics:
    """Metrics for a complete pipeline execution"""
    care_request_id: str
    total_duration_seconds: float
    agent_metrics: List[AgentMetrics]
    task_count: int
    success: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
    evaluation_scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """
    Collects and aggregates metrics from agent executions
    
    Provides:
    - Real-time metrics collection
    - Aggregation across multiple runs
    - Statistical summaries
    - Export to various formats
    """
    
    def __init__(self):
        """Initialize metrics collector"""
        self.pipeline_metrics: List[PipelineMetrics] = []
        self.agent_metrics: List[AgentMetrics] = []
    
    def record_agent_metrics(self, metrics: AgentMetrics):
        """
        Record metrics from a single agent execution
        
        Args:
            metrics: AgentMetrics object
        """
        self.agent_metrics.append(metrics)
        logger.info(
            f"Recorded metrics for {metrics.agent_name}: "
            f"duration={metrics.duration_seconds:.2f}s, success={metrics.success}"
        )
    
    def record_pipeline_metrics(self, metrics: PipelineMetrics):
        """
        Record metrics from a complete pipeline execution
        
        Args:
            metrics: PipelineMetrics object
        """
        self.pipeline_metrics.append(metrics)
        logger.info(
            f"Recorded pipeline metrics for {metrics.care_request_id}: "
            f"duration={metrics.total_duration_seconds:.2f}s, tasks={metrics.task_count}"
        )
    
    def get_agent_statistics(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistical summary of agent performance
        
        Args:
            agent_name: Optional agent name to filter by
            
        Returns:
            Dictionary with statistical summaries
        """
        metrics = self.agent_metrics
        if agent_name:
            metrics = [m for m in metrics if m.agent_name == agent_name]
        
        if not metrics:
            return {}
        
        durations = [m.duration_seconds for m in metrics]
        successes = [m.success for m in metrics]
        
        return {
            "agent_name": agent_name or "all",
            "execution_count": len(metrics),
            "success_rate": sum(successes) / len(successes) if successes else 0,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "total_duration": sum(durations),
            "error_count": sum(1 for m in metrics if not m.success)
        }
    
    def get_pipeline_statistics(self) -> Dict[str, Any]:
        """
        Get statistical summary of pipeline performance
        
        Returns:
            Dictionary with statistical summaries
        """
        if not self.pipeline_metrics:
            return {}
        
        durations = [m.total_duration_seconds for m in self.pipeline_metrics]
        task_counts = [m.task_count for m in self.pipeline_metrics]
        successes = [m.success for m in self.pipeline_metrics]
        
        return {
            "pipeline_count": len(self.pipeline_metrics),
            "success_rate": sum(successes) / len(successes) if successes else 0,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "avg_task_count": sum(task_counts) / len(task_counts) if task_counts else 0,
            "min_task_count": min(task_counts) if task_counts else 0,
            "max_task_count": max(task_counts) if task_counts else 0
        }
    
    def get_evaluation_summary(self) -> Dict[str, Any]:
        """
        Get summary of evaluation scores across all pipelines
        
        Returns:
            Dictionary with evaluation score summaries
        """
        if not self.pipeline_metrics:
            return {}
        
        # Aggregate evaluation scores
        all_scores: Dict[str, List[float]] = {}
        
        for pipeline in self.pipeline_metrics:
            for eval_name, score in pipeline.evaluation_scores.items():
                if eval_name not in all_scores:
                    all_scores[eval_name] = []
                all_scores[eval_name].append(score)
        
        # Calculate statistics for each evaluation metric
        summary = {}
        for eval_name, scores in all_scores.items():
            summary[eval_name] = {
                "count": len(scores),
                "avg": sum(scores) / len(scores) if scores else 0,
                "min": min(scores) if scores else 0,
                "max": max(scores) if scores else 0,
                "scores": scores
            }
        
        return summary
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """
        Get comprehensive metrics report
        
        Returns:
            Dictionary with all metrics and statistics
        """
        # Get statistics for each agent
        agent_names = set(m.agent_name for m in self.agent_metrics)
        agent_stats = {
            agent: self.get_agent_statistics(agent)
            for agent in agent_names
        }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_pipelines": len(self.pipeline_metrics),
                "total_agent_executions": len(self.agent_metrics),
                "unique_agents": len(agent_names)
            },
            "pipeline_statistics": self.get_pipeline_statistics(),
            "agent_statistics": agent_stats,
            "evaluation_summary": self.get_evaluation_summary()
        }
    
    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export all collected metrics to a dictionary
        
        Returns:
            Dictionary with all raw metrics
        """
        return {
            "pipeline_metrics": [
                {
                    "care_request_id": m.care_request_id,
                    "total_duration_seconds": m.total_duration_seconds,
                    "task_count": m.task_count,
                    "success": m.success,
                    "timestamp": m.timestamp.isoformat(),
                    "evaluation_scores": m.evaluation_scores,
                    "metadata": m.metadata,
                    "agent_metrics": [
                        {
                            "agent_name": am.agent_name,
                            "task_name": am.task_name,
                            "duration_seconds": am.duration_seconds,
                            "success": am.success,
                            "input_length": am.input_length,
                            "output_length": am.output_length,
                            "timestamp": am.timestamp.isoformat(),
                            "error": am.error,
                            "custom_metrics": am.custom_metrics
                        }
                        for am in m.agent_metrics
                    ]
                }
                for m in self.pipeline_metrics
            ]
        }
    
    def reset(self):
        """Reset all collected metrics"""
        self.pipeline_metrics.clear()
        self.agent_metrics.clear()
        logger.info("Metrics collector reset")


# Global metrics collector instance
metrics_collector = MetricsCollector()
