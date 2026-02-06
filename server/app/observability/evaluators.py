"""
Custom evaluators for Care Circles agent outputs

Provides specialized evaluators for assessing:
- Task quality and actionability
- Boundary compliance and safety
- Completeness of care plans
- Clarity and understandability
- Overall pipeline performance
"""

import logging
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

try:
    from opik.evaluation.metrics import base_metric, score_result
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    # Create dummy decorators for when Opik is not available
    def base_metric(func):
        return func
    def score_result(func):
        return func

from app.models.domain import CareTask, NeedsMap, ReviewPacket

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Result of an evaluation"""
    score: float  # 0.0 to 1.0
    reason: str
    metadata: Optional[Dict[str, Any]] = None


class TaskQualityEvaluator:
    """
    Evaluates the quality of generated care tasks
    
    Criteria:
    - Actionability: Is the task specific and actionable?
    - Clarity: Is the description clear and understandable?
    - Appropriateness: Is the task appropriate for volunteers?
    - Context: Does the task provide sufficient context?
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize evaluator
        
        Args:
            llm_client: Optional LLM client for LLM-as-judge evaluation
        """
        self.llm_client = llm_client
    
    def evaluate_task(self, task: CareTask, original_request: str) -> EvaluationResult:
        """
        Evaluate a single care task
        
        Args:
            task: The care task to evaluate
            original_request: The original care request narrative
            
        Returns:
            EvaluationResult with score and reasoning
        """
        score = 0.0
        reasons = []
        
        # Check actionability (has specific verbs and details)
        if self._is_actionable(task):
            score += 0.25
            reasons.append("Task is actionable")
        else:
            reasons.append("Task lacks actionability")
        
        # Check clarity (description is clear and not too vague)
        if self._is_clear(task):
            score += 0.25
            reasons.append("Task is clear")
        else:
            reasons.append("Task lacks clarity")
        
        # Check appropriateness (suitable for volunteers)
        if self._is_appropriate(task):
            score += 0.25
            reasons.append("Task is appropriate")
        else:
            reasons.append("Task may not be appropriate")
        
        # Check context (provides enough background)
        if self._has_context(task):
            score += 0.25
            reasons.append("Task has sufficient context")
        else:
            reasons.append("Task lacks context")
        
        return EvaluationResult(
            score=score,
            reason="; ".join(reasons),
            metadata={
                "task_id": task.id,
                "task_title": task.title,
                "category": task.category,
                "priority": task.priority
            }
        )
    
    def evaluate_tasks(self, tasks: List[CareTask], original_request: str) -> EvaluationResult:
        """
        Evaluate a list of care tasks
        
        Args:
            tasks: List of care tasks to evaluate
            original_request: The original care request narrative
            
        Returns:
            Aggregated EvaluationResult
        """
        if not tasks:
            return EvaluationResult(
                score=0.0,
                reason="No tasks generated",
                metadata={"task_count": 0}
            )
        
        # Evaluate each task
        task_results = [self.evaluate_task(task, original_request) for task in tasks]
        
        # Calculate average score
        avg_score = sum(r.score for r in task_results) / len(task_results)
        
        # Count high-quality tasks (score >= 0.75)
        high_quality_count = sum(1 for r in task_results if r.score >= 0.75)
        
        return EvaluationResult(
            score=avg_score,
            reason=f"{high_quality_count}/{len(tasks)} tasks are high quality (>= 0.75)",
            metadata={
                "task_count": len(tasks),
                "high_quality_count": high_quality_count,
                "avg_score": avg_score,
                "task_scores": [r.score for r in task_results]
            }
        )
    
    def _is_actionable(self, task: CareTask) -> bool:
        """Check if task is actionable"""
        # Check for action verbs
        action_verbs = [
            "prepare", "deliver", "drive", "pick up", "drop off",
            "call", "visit", "help", "assist", "organize", "schedule",
            "buy", "purchase", "arrange", "coordinate", "provide"
        ]
        title_lower = task.title.lower()
        desc_lower = task.description.lower()
        
        has_action_verb = any(verb in title_lower or verb in desc_lower for verb in action_verbs)
        has_sufficient_length = len(task.description) >= 20
        
        return has_action_verb and has_sufficient_length
    
    def _is_clear(self, task: CareTask) -> bool:
        """Check if task is clear"""
        # Check for vague words
        vague_words = ["maybe", "possibly", "perhaps", "might", "could be", "unclear"]
        desc_lower = task.description.lower()
        
        has_vague_words = any(word in desc_lower for word in vague_words)
        has_sufficient_detail = len(task.description.split()) >= 10
        
        return not has_vague_words and has_sufficient_detail
    
    def _is_appropriate(self, task: CareTask) -> bool:
        """Check if task is appropriate for volunteers"""
        # Flag inappropriate tasks (medical, financial, etc.)
        inappropriate_keywords = [
            "medication", "prescribe", "diagnose", "surgery", "medical procedure",
            "bank account", "credit card", "password", "legal document"
        ]
        desc_lower = task.description.lower()
        title_lower = task.title.lower()
        
        has_inappropriate = any(
            keyword in desc_lower or keyword in title_lower 
            for keyword in inappropriate_keywords
        )
        
        return not has_inappropriate
    
    def _has_context(self, task: CareTask) -> bool:
        """Check if task has sufficient context"""
        # Check if description explains the "why" or provides background
        context_indicators = ["because", "since", "to help", "in order to", "for", "needs"]
        desc_lower = task.description.lower()
        
        has_context_indicator = any(indicator in desc_lower for indicator in context_indicators)
        has_category = bool(task.category and task.category != "general")
        
        return has_context_indicator or has_category


class BoundaryComplianceEvaluator:
    """
    Evaluates compliance with stated boundaries and constraints
    
    Ensures that generated tasks respect:
    - Stated boundaries from the care request
    - Privacy and dignity constraints
    - Appropriate scope for volunteer work
    """
    
    def evaluate(
        self,
        tasks: List[CareTask],
        care_request_narrative: str,
        constraints: Optional[str] = None,
        boundaries: Optional[str] = None
    ) -> EvaluationResult:
        """
        Evaluate boundary compliance
        
        Args:
            tasks: List of care tasks
            care_request_narrative: Original narrative
            constraints: Stated constraints
            boundaries: Stated boundaries
            
        Returns:
            EvaluationResult
        """
        if not tasks:
            return EvaluationResult(score=1.0, reason="No tasks to evaluate")
        
        violations = []
        
        # Check for common boundary violations
        for task in tasks:
            task_text = f"{task.title} {task.description}".lower()
            
            # Check for medical overreach
            if any(word in task_text for word in ["administer", "inject", "prescribe", "diagnose"]):
                violations.append(f"Medical overreach in task: {task.title}")
            
            # Check for financial overreach
            if any(word in task_text for word in ["bank", "account", "credit card", "password"]):
                violations.append(f"Financial overreach in task: {task.title}")
            
            # Check against stated boundaries
            if boundaries:
                boundaries_lower = boundaries.lower()
                # Look for explicit "no" statements
                if "no visitors" in boundaries_lower and "visit" in task_text:
                    violations.append(f"Violates 'no visitors' boundary: {task.title}")
                if "no phone calls" in boundaries_lower and "call" in task_text:
                    violations.append(f"Violates 'no phone calls' boundary: {task.title}")
        
        # Calculate score
        if not violations:
            score = 1.0
            reason = "All tasks comply with boundaries"
        else:
            score = max(0.0, 1.0 - (len(violations) * 0.2))
            reason = f"Found {len(violations)} boundary violations"
        
        return EvaluationResult(
            score=score,
            reason=reason,
            metadata={
                "violations": violations,
                "violation_count": len(violations)
            }
        )


class CompletenessEvaluator:
    """
    Evaluates completeness of the care plan
    
    Checks if the generated tasks adequately cover:
    - All identified needs from the needs map
    - Different categories of support
    - Appropriate priority distribution
    """
    
    def evaluate(
        self,
        tasks: List[CareTask],
        needs_map: NeedsMap
    ) -> EvaluationResult:
        """
        Evaluate completeness of care plan
        
        Args:
            tasks: List of care tasks
            needs_map: The needs map from A1
            
        Returns:
            EvaluationResult
        """
        if not tasks:
            return EvaluationResult(
                score=0.0,
                reason="No tasks generated",
                metadata={"task_count": 0}
            )
        
        score = 0.0
        reasons = []
        
        # Check category coverage (should have diverse categories)
        categories = set(task.category for task in tasks)
        if len(categories) >= 3:
            score += 0.3
            reasons.append(f"Good category diversity ({len(categories)} categories)")
        else:
            reasons.append(f"Limited category diversity ({len(categories)} categories)")
        
        # Check priority distribution (should have mix of priorities)
        priorities = [task.priority for task in tasks]
        priority_set = set(priorities)
        if len(priority_set) >= 2:
            score += 0.2
            reasons.append("Appropriate priority distribution")
        else:
            reasons.append("Limited priority distribution")
        
        # Check task count (should have reasonable number)
        task_count = len(tasks)
        if 5 <= task_count <= 20:
            score += 0.3
            reasons.append(f"Appropriate task count ({task_count})")
        elif task_count < 5:
            reasons.append(f"Too few tasks ({task_count})")
        else:
            score += 0.15
            reasons.append(f"Many tasks ({task_count})")
        
        # Check if needs are addressed (simple keyword matching)
        if needs_map.identified_needs:
            needs_text = json.dumps(needs_map.identified_needs).lower()
            tasks_text = " ".join(f"{t.title} {t.description}" for t in tasks).lower()
            
            # Extract key needs (simple approach)
            need_keywords = self._extract_keywords(needs_text)
            addressed_needs = sum(1 for keyword in need_keywords if keyword in tasks_text)
            
            if need_keywords:
                coverage_ratio = addressed_needs / len(need_keywords)
                score += coverage_ratio * 0.2
                reasons.append(f"Addresses {addressed_needs}/{len(need_keywords)} identified needs")
        
        return EvaluationResult(
            score=min(score, 1.0),
            reason="; ".join(reasons),
            metadata={
                "task_count": task_count,
                "category_count": len(categories),
                "categories": list(categories),
                "priority_distribution": {p: priorities.count(p) for p in priority_set}
            }
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key needs keywords from text"""
        # Simple keyword extraction (could be enhanced with NLP)
        keywords = []
        important_words = [
            "meal", "food", "transport", "ride", "visit", "company",
            "clean", "laundry", "shop", "grocery", "medication", "appointment",
            "call", "check", "help", "assist", "support"
        ]
        
        for word in important_words:
            if word in text:
                keywords.append(word)
        
        return keywords


class ClarityEvaluator:
    """
    Evaluates clarity and understandability of outputs
    
    Checks:
    - Language simplicity
    - Structure and organization
    - Absence of jargon
    - Readability
    """
    
    def evaluate_review_packet(self, review_packet: ReviewPacket) -> EvaluationResult:
        """
        Evaluate clarity of review packet
        
        Args:
            review_packet: The review packet from A5
            
        Returns:
            EvaluationResult
        """
        score = 0.0
        reasons = []
        
        # Check summary clarity
        if review_packet.summary:
            summary_words = len(review_packet.summary.split())
            if 50 <= summary_words <= 300:
                score += 0.3
                reasons.append("Summary is appropriate length")
            else:
                reasons.append(f"Summary length suboptimal ({summary_words} words)")
        
        # Check if agent notes are provided
        if review_packet.agent_notes:
            score += 0.2
            reasons.append("Agent notes provided")
        else:
            reasons.append("No agent notes")
        
        # Check task organization
        if review_packet.draft_tasks:
            # Check if tasks have consistent structure
            has_descriptions = all(t.description for t in review_packet.draft_tasks)
            has_categories = all(t.category for t in review_packet.draft_tasks)
            
            if has_descriptions and has_categories:
                score += 0.3
                reasons.append("Tasks are well-structured")
            else:
                reasons.append("Tasks lack consistent structure")
        
        # Check readability (simple heuristic)
        combined_text = f"{review_packet.summary} {review_packet.agent_notes}"
        avg_word_length = sum(len(word) for word in combined_text.split()) / max(len(combined_text.split()), 1)
        
        if avg_word_length <= 6:  # Simple language
            score += 0.2
            reasons.append("Language is simple and clear")
        else:
            reasons.append("Language could be simpler")
        
        return EvaluationResult(
            score=min(score, 1.0),
            reason="; ".join(reasons),
            metadata={
                "summary_word_count": len(review_packet.summary.split()) if review_packet.summary else 0,
                "has_agent_notes": bool(review_packet.agent_notes),
                "task_count": len(review_packet.draft_tasks),
                "avg_word_length": avg_word_length
            }
        )


class PipelinePerformanceEvaluator:
    """
    Evaluates overall pipeline performance
    
    Tracks:
    - Execution time per agent
    - Success rates
    - Error patterns
    - Resource utilization
    """
    
    def __init__(self):
        self.agent_timings: Dict[str, List[float]] = {}
        self.agent_errors: Dict[str, List[str]] = {}
    
    def record_agent_execution(
        self,
        agent_name: str,
        duration_seconds: float,
        success: bool,
        error: Optional[str] = None
    ):
        """Record an agent execution for performance tracking"""
        if agent_name not in self.agent_timings:
            self.agent_timings[agent_name] = []
            self.agent_errors[agent_name] = []
        
        self.agent_timings[agent_name].append(duration_seconds)
        
        if not success and error:
            self.agent_errors[agent_name].append(error)
    
    def evaluate_pipeline(self, total_duration: float) -> EvaluationResult:
        """
        Evaluate overall pipeline performance
        
        Args:
            total_duration: Total pipeline execution time in seconds
            
        Returns:
            EvaluationResult
        """
        score = 1.0
        reasons = []
        
        # Check execution time (should be reasonable)
        if total_duration < 60:  # Less than 1 minute
            reasons.append(f"Fast execution ({total_duration:.1f}s)")
        elif total_duration < 180:  # Less than 3 minutes
            score -= 0.1
            reasons.append(f"Moderate execution time ({total_duration:.1f}s)")
        else:
            score -= 0.3
            reasons.append(f"Slow execution ({total_duration:.1f}s)")
        
        # Check for errors
        total_errors = sum(len(errors) for errors in self.agent_errors.values())
        if total_errors > 0:
            score -= 0.3 * min(total_errors, 3)
            reasons.append(f"{total_errors} errors encountered")
        else:
            reasons.append("No errors")
        
        # Check agent balance (no single agent should dominate time)
        if self.agent_timings:
            timings = [sum(times) for times in self.agent_timings.values()]
            if timings:
                max_time = max(timings)
                total_time = sum(timings)
                if max_time / total_time < 0.5:  # No agent takes more than 50%
                    reasons.append("Balanced agent execution")
                else:
                    score -= 0.1
                    reasons.append("Unbalanced agent execution")
        
        return EvaluationResult(
            score=max(score, 0.0),
            reason="; ".join(reasons),
            metadata={
                "total_duration": total_duration,
                "agent_timings": {
                    agent: {
                        "count": len(times),
                        "total": sum(times),
                        "avg": sum(times) / len(times) if times else 0
                    }
                    for agent, times in self.agent_timings.items()
                },
                "total_errors": total_errors,
                "error_details": self.agent_errors
            }
        )
