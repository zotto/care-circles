"""
Instrumented Agent Orchestrator with Opik Integration

Wraps the standard AgentOrchestrator with comprehensive observability:
- Traces all agent executions
- Collects metrics at each stage
- Runs evaluations on outputs
- Logs experiments for comparison
"""

import logging
from datetime import datetime
from typing import Optional, Callable, Dict, Any

from app.models.domain import CareRequest, ReviewPacket
from app.services.agent_orchestrator import AgentOrchestrator
from app.observability.opik_client import opik_client
from app.observability.opik_tracker import log_to_opik
from app.observability.evaluators import (
    TaskQualityEvaluator,
    BoundaryComplianceEvaluator,
    CompletenessEvaluator,
    ClarityEvaluator,
    PipelinePerformanceEvaluator
)
from app.observability.metrics import (
    MetricsCollector,
    AgentMetrics,
    PipelineMetrics,
    metrics_collector
)

logger = logging.getLogger(__name__)


class InstrumentedOrchestrator:
    """
    Orchestrator with full Opik observability integration
    
    Wraps the standard AgentOrchestrator to add:
    - Distributed tracing for each agent
    - Real-time metrics collection
    - Automated evaluation of outputs
    - Experiment tracking
    """
    
    def __init__(self, orchestrator: Optional[AgentOrchestrator] = None):
        """
        Initialize instrumented orchestrator
        
        Args:
            orchestrator: Optional existing orchestrator, or create new one
        """
        self.orchestrator = orchestrator or AgentOrchestrator()
        self.task_quality_evaluator = TaskQualityEvaluator()
        self.boundary_evaluator = BoundaryComplianceEvaluator()
        self.completeness_evaluator = CompletenessEvaluator()
        self.clarity_evaluator = ClarityEvaluator()
        self.performance_evaluator = PipelinePerformanceEvaluator()
        self.metrics_collector = metrics_collector
        
        logger.info("InstrumentedOrchestrator initialized with Opik integration")
    
    def run_pipeline_sync(
        self,
        care_request: CareRequest,
        progress_callback: Optional[Callable] = None,
        experiment_name: Optional[str] = None,
        experiment_params: Optional[Dict[str, Any]] = None
    ) -> ReviewPacket:
        """
        Execute pipeline with full observability
        
        Args:
            care_request: The care request to process
            progress_callback: Optional callback for progress updates
            experiment_name: Optional experiment name for tracking
            experiment_params: Optional experiment parameters
            
        Returns:
            ReviewPacket with the final care plan
        """
        start_time = datetime.utcnow()
        pipeline_start = start_time
        agent_metrics_list = []
        
        # Log experiment if name provided
        experiment_id = None
        if experiment_name and opik_client.is_enabled():
            experiment_id = opik_client.log_experiment(
                experiment_name=experiment_name,
                parameters=experiment_params or {
                    "model": "gpt-4",
                    "care_request_id": care_request.id
                },
                metadata={
                    "care_request_id": care_request.id,
                    "timestamp": start_time.isoformat()
                }
            )
        
        try:
            # A1: Intake & Needs Analysis
            logger.info("=== A1: Intake & Needs Analysis (Instrumented) ===")
            a1_start = datetime.utcnow()
            
            if progress_callback:
                progress_callback("A1", "running")
            
            needs_map = self.orchestrator._run_agent_a1_sync(care_request)
            
            a1_duration = (datetime.utcnow() - a1_start).total_seconds()
            
            # Log to Opik dashboard
            log_to_opik(
                name="A1_intake_analyst_analyze_needs",
                input_data={
                    "narrative": care_request.narrative[:500],
                    "constraints": care_request.constraints,
                    "boundaries": care_request.boundaries
                },
                output_data={
                    "summary": needs_map.summary[:500],
                    "identified_needs_count": len(needs_map.identified_needs),
                    "risks_count": len(needs_map.risks) if needs_map.risks else 0
                },
                metadata={
                    "agent_name": "A1_intake_analyst",
                    "task_name": "analyze_needs",
                    "care_request_id": care_request.id,
                    "experiment_id": experiment_id,
                    "duration_seconds": a1_duration,
                    "identified_needs_count": len(needs_map.identified_needs),
                    "success": True
                }
            )
            
            if progress_callback:
                progress_callback("A1", "completed")
            
            # Record A1 metrics
            agent_metrics_list.append(AgentMetrics(
                agent_name="A1_intake_analyst",
                task_name="analyze_needs",
                duration_seconds=a1_duration,
                success=True,
                input_length=len(care_request.narrative),
                output_length=len(str(needs_map)),
                custom_metrics={
                    "identified_needs_count": len(needs_map.identified_needs)
                }
            ))
            self.performance_evaluator.record_agent_execution(
                "A1_intake_analyst", a1_duration, True
            )
            
            # A2: Task Generation
            logger.info("=== A2: Task Generation (Instrumented) ===")
            a2_start = datetime.utcnow()
            
            if progress_callback:
                progress_callback("A2", "running")
            
            draft_tasks = self.orchestrator._run_agent_a2_sync(needs_map, care_request)
            
            a2_duration = (datetime.utcnow() - a2_start).total_seconds()
            
            # Evaluate task quality
            quality_eval = self.task_quality_evaluator.evaluate_tasks(
                draft_tasks, care_request.narrative
            )
            
            # Log to Opik dashboard
            log_to_opik(
                name="A2_task_generator_generate_tasks",
                input_data={
                    "needs_summary": needs_map.summary[:500],
                    "identified_needs_count": len(needs_map.identified_needs)
                },
                output_data={
                    "task_count": len(draft_tasks),
                    "tasks_preview": [{"title": t.title, "category": t.category, "priority": t.priority} for t in draft_tasks[:3]],
                    "quality_score": quality_eval.score
                },
                metadata={
                    "agent_name": "A2_task_generator",
                    "task_name": "generate_tasks",
                    "care_request_id": care_request.id,
                    "needs_map_id": needs_map.id,
                    "experiment_id": experiment_id,
                    "duration_seconds": a2_duration,
                    "task_count": len(draft_tasks),
                    "quality_score": quality_eval.score,
                    "success": True
                }
            )
            
            if progress_callback:
                progress_callback("A2", "completed")
            
            # Record A2 metrics
            agent_metrics_list.append(AgentMetrics(
                agent_name="A2_task_generator",
                task_name="generate_tasks",
                duration_seconds=a2_duration,
                success=True,
                input_length=len(needs_map.summary),
                output_length=len(str(draft_tasks)),
                custom_metrics={
                    "task_count": len(draft_tasks),
                    "quality_score": quality_eval.score
                }
            ))
            self.performance_evaluator.record_agent_execution(
                "A2_task_generator", a2_duration, True
            )
            
            # A3: Guardian & Quality Pass
            logger.info("=== A3: Guardian & Quality Pass (Instrumented) ===")
            a3_start = datetime.utcnow()
            
            if progress_callback:
                progress_callback("A3", "running")
            
            reviewed_tasks = self.orchestrator._run_agent_a3_sync(draft_tasks, care_request)
            
            a3_duration = (datetime.utcnow() - a3_start).total_seconds()
            
            # Evaluate boundary compliance
            boundary_eval = self.boundary_evaluator.evaluate(
                reviewed_tasks,
                care_request.narrative,
                care_request.constraints,
                care_request.boundaries
            )
            
            # Log to Opik dashboard
            log_to_opik(
                name="A3_guardian_reviewer_review_quality",
                input_data={
                    "task_count": len(draft_tasks),
                    "constraints": care_request.constraints,
                    "boundaries": care_request.boundaries
                },
                output_data={
                    "reviewed_task_count": len(reviewed_tasks),
                    "boundary_compliance_score": boundary_eval.score,
                    "violations": boundary_eval.metadata.get("violations", []) if boundary_eval.metadata else []
                },
                metadata={
                    "agent_name": "A3_guardian_reviewer",
                    "task_name": "review_quality",
                    "care_request_id": care_request.id,
                    "experiment_id": experiment_id,
                    "duration_seconds": a3_duration,
                    "reviewed_task_count": len(reviewed_tasks),
                    "boundary_compliance_score": boundary_eval.score,
                    "success": True
                }
            )
            
            if progress_callback:
                progress_callback("A3", "completed")
            
            # Record A3 metrics
            agent_metrics_list.append(AgentMetrics(
                agent_name="A3_guardian_reviewer",
                task_name="review_quality",
                duration_seconds=a3_duration,
                success=True,
                input_length=len(str(draft_tasks)),
                output_length=len(str(reviewed_tasks)),
                custom_metrics={
                    "reviewed_task_count": len(reviewed_tasks),
                    "boundary_compliance_score": boundary_eval.score
                }
            ))
            self.performance_evaluator.record_agent_execution(
                "A3_guardian_reviewer", a3_duration, True
            )
            
            # A4: Optimization
            logger.info("=== A4: Optimization (Instrumented) ===")
            a4_start = datetime.utcnow()
            
            if progress_callback:
                progress_callback("A4", "running")
            
            optimized_tasks = self.orchestrator._run_agent_a4_sync(reviewed_tasks, care_request)
            
            a4_duration = (datetime.utcnow() - a4_start).total_seconds()
            
            # Evaluate completeness
            completeness_eval = self.completeness_evaluator.evaluate(
                optimized_tasks, needs_map
            )
            
            # Log to Opik dashboard
            log_to_opik(
                name="A4_optimization_specialist_optimize_plan",
                input_data={
                    "task_count": len(reviewed_tasks),
                    "categories": list(set(t.category for t in reviewed_tasks))
                },
                output_data={
                    "optimized_task_count": len(optimized_tasks),
                    "completeness_score": completeness_eval.score,
                    "categories": list(set(t.category for t in optimized_tasks))
                },
                metadata={
                    "agent_name": "A4_optimization_specialist",
                    "task_name": "optimize_plan",
                    "care_request_id": care_request.id,
                    "experiment_id": experiment_id,
                    "duration_seconds": a4_duration,
                    "optimized_task_count": len(optimized_tasks),
                    "completeness_score": completeness_eval.score,
                    "success": True
                }
            )
            
            if progress_callback:
                progress_callback("A4", "completed")
            
            # Record A4 metrics
            agent_metrics_list.append(AgentMetrics(
                agent_name="A4_optimization_specialist",
                task_name="optimize_plan",
                duration_seconds=a4_duration,
                success=True,
                input_length=len(str(reviewed_tasks)),
                output_length=len(str(optimized_tasks)),
                custom_metrics={
                    "optimized_task_count": len(optimized_tasks),
                    "completeness_score": completeness_eval.score
                }
            ))
            self.performance_evaluator.record_agent_execution(
                "A4_optimization_specialist", a4_duration, True
            )
            
            # A5: Review Packet Assembly
            logger.info("=== A5: Review Packet Assembly (Instrumented) ===")
            a5_start = datetime.utcnow()
            
            if progress_callback:
                progress_callback("A5", "running")
            
            review_packet = self.orchestrator._run_agent_a5_sync(
                optimized_tasks, needs_map, care_request
            )
            
            a5_duration = (datetime.utcnow() - a5_start).total_seconds()
            
            # Evaluate clarity
            clarity_eval = self.clarity_evaluator.evaluate_review_packet(review_packet)
            
            # Log to Opik dashboard
            log_to_opik(
                name="A5_review_assembler_assemble_review",
                input_data={
                    "task_count": len(optimized_tasks),
                    "needs_summary": needs_map.summary[:300]
                },
                output_data={
                    "final_task_count": len(review_packet.draft_tasks),
                    "summary_length": len(review_packet.summary) if review_packet.summary else 0,
                    "has_agent_notes": bool(review_packet.agent_notes),
                    "clarity_score": clarity_eval.score
                },
                metadata={
                    "agent_name": "A5_review_assembler",
                    "task_name": "assemble_review",
                    "care_request_id": care_request.id,
                    "experiment_id": experiment_id,
                    "duration_seconds": a5_duration,
                    "final_task_count": len(review_packet.draft_tasks),
                    "clarity_score": clarity_eval.score,
                    "success": True
                }
            )
            
            if progress_callback:
                progress_callback("A5", "completed")
            
            # Record A5 metrics
            agent_metrics_list.append(AgentMetrics(
                agent_name="A5_review_assembler",
                task_name="assemble_review",
                duration_seconds=a5_duration,
                success=True,
                input_length=len(str(optimized_tasks)),
                output_length=len(str(review_packet)),
                custom_metrics={
                    "final_task_count": len(review_packet.draft_tasks),
                    "clarity_score": clarity_eval.score
                }
            ))
            self.performance_evaluator.record_agent_execution(
                "A5_review_assembler", a5_duration, True
            )
            
            # Calculate total pipeline duration
            total_duration = (datetime.utcnow() - pipeline_start).total_seconds()
            
            # Evaluate overall pipeline performance
            performance_eval = self.performance_evaluator.evaluate_pipeline(total_duration)
            
            # Collect all evaluation scores
            evaluation_scores = {
                "task_quality": quality_eval.score,
                "boundary_compliance": boundary_eval.score,
                "completeness": completeness_eval.score,
                "clarity": clarity_eval.score,
                "performance": performance_eval.score,
                "overall": (
                    quality_eval.score * 0.3 +
                    boundary_eval.score * 0.25 +
                    completeness_eval.score * 0.25 +
                    clarity_eval.score * 0.1 +
                    performance_eval.score * 0.1
                )
            }
            
            # Log pipeline metrics
            pipeline_metrics = PipelineMetrics(
                care_request_id=care_request.id,
                total_duration_seconds=total_duration,
                agent_metrics=agent_metrics_list,
                task_count=len(review_packet.draft_tasks),
                success=True,
                evaluation_scores=evaluation_scores,
                metadata={
                    "experiment_id": experiment_id,
                    "experiment_name": experiment_name,
                    "needs_count": len(needs_map.identified_needs)
                }
            )
            self.metrics_collector.record_pipeline_metrics(pipeline_metrics)
            
            # Log complete pipeline to Opik dashboard
            log_to_opik(
                name="PIPELINE_COMPLETE_care_plan_generation",
                input_data={
                    "care_request_id": care_request.id,
                    "narrative_length": len(care_request.narrative),
                    "has_constraints": bool(care_request.constraints),
                    "has_boundaries": bool(care_request.boundaries)
                },
                output_data={
                    "success": True,
                    "final_task_count": len(review_packet.draft_tasks),
                    "evaluation_scores": evaluation_scores,
                    "agent_durations": {
                        "A1": a1_duration,
                        "A2": a2_duration,
                        "A3": a3_duration,
                        "A4": a4_duration,
                        "A5": a5_duration
                    }
                },
                metadata={
                    "pipeline_name": "care_plan_generation",
                    "care_request_id": care_request.id,
                    "experiment_id": experiment_id,
                    "experiment_name": experiment_name,
                    "total_duration_seconds": total_duration,
                    "task_count": len(review_packet.draft_tasks),
                    "needs_count": len(needs_map.identified_needs),
                    **evaluation_scores,
                    "success": True
                }
            )
            
            logger.info(
                f"Pipeline completed successfully in {total_duration:.2f}s. "
                f"Overall score: {evaluation_scores['overall']:.3f}"
            )
            
            return review_packet
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            
            # Record failure metrics
            total_duration = (datetime.utcnow() - pipeline_start).total_seconds()
            pipeline_metrics = PipelineMetrics(
                care_request_id=care_request.id,
                total_duration_seconds=total_duration,
                agent_metrics=agent_metrics_list,
                task_count=0,
                success=False,
                metadata={
                    "experiment_id": experiment_id,
                    "error": str(e)
                }
            )
            self.metrics_collector.record_pipeline_metrics(pipeline_metrics)
            
            raise
