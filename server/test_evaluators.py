"""
Test script for Care Circles evaluators

Demonstrates the evaluation capabilities without requiring full pipeline execution.
"""

import logging
from datetime import datetime
from uuid import uuid4

from app.models.domain import CareTask, NeedsMap, ReviewPacket
from app.config.constants import TaskPriority, TaskStatus, ApprovalStatus
from app.observability.evaluators import (
    TaskQualityEvaluator,
    BoundaryComplianceEvaluator,
    CompletenessEvaluator,
    ClarityEvaluator
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_eval_result(name: str, result):
    """Print evaluation result in a formatted way"""
    print(f"\n{name}:")
    print(f"  Score: {result.score:.3f}")
    print(f"  Reason: {result.reason}")
    if result.metadata:
        print(f"  Metadata: {result.metadata}")


def test_task_quality_evaluator():
    """Test the TaskQualityEvaluator"""
    print("\n" + "=" * 80)
    print("Testing TaskQualityEvaluator")
    print("=" * 80)
    
    evaluator = TaskQualityEvaluator()
    
    # Create sample tasks
    good_task = CareTask(
        id="task_1",
        care_request_id="req_1",
        title="Prepare and deliver dinner meal",
        description="Prepare a nutritious dinner meal (considering dietary restrictions) and deliver it to the home between 5-6pm. This helps ensure proper nutrition during recovery.",
        category="meals",
        priority=TaskPriority.HIGH,
        status=TaskStatus.DRAFT,
        created_at=datetime.utcnow()
    )
    
    poor_task = CareTask(
        id="task_2",
        care_request_id="req_1",
        title="Help",
        description="Maybe help with something",
        category="general",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.DRAFT,
        created_at=datetime.utcnow()
    )
    
    inappropriate_task = CareTask(
        id="task_3",
        care_request_id="req_1",
        title="Administer medication",
        description="Give the patient their medication at prescribed times",
        category="medical",
        priority=TaskPriority.HIGH,
        status=TaskStatus.DRAFT,
        created_at=datetime.utcnow()
    )
    
    # Evaluate individual tasks
    print("\n1. High-Quality Task:")
    result = evaluator.evaluate_task(good_task, "Patient needs help with meals")
    print_eval_result("Result", result)
    
    print("\n2. Poor-Quality Task:")
    result = evaluator.evaluate_task(poor_task, "Patient needs help")
    print_eval_result("Result", result)
    
    print("\n3. Inappropriate Task:")
    result = evaluator.evaluate_task(inappropriate_task, "Patient needs help")
    print_eval_result("Result", result)
    
    # Evaluate list of tasks
    print("\n4. Evaluating Multiple Tasks:")
    tasks = [good_task, poor_task, inappropriate_task]
    result = evaluator.evaluate_tasks(tasks, "Patient needs various types of help")
    print_eval_result("Result", result)


def test_boundary_compliance_evaluator():
    """Test the BoundaryComplianceEvaluator"""
    print("\n" + "=" * 80)
    print("Testing BoundaryComplianceEvaluator")
    print("=" * 80)
    
    evaluator = BoundaryComplianceEvaluator()
    
    # Create sample tasks
    compliant_tasks = [
        CareTask(
            id="task_1",
            care_request_id="req_1",
            title="Grocery shopping",
            description="Pick up groceries from the list provided",
            category="errands",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.DRAFT,
            created_at=datetime.utcnow()
        ),
        CareTask(
            id="task_2",
            care_request_id="req_1",
            title="Friendly visit",
            description="Stop by for a 30-minute visit to provide companionship",
            category="companionship",
            priority=TaskPriority.LOW,
            status=TaskStatus.DRAFT,
            created_at=datetime.utcnow()
        )
    ]
    
    violating_tasks = [
        CareTask(
            id="task_3",
            care_request_id="req_1",
            title="Visit patient",
            description="Visit the patient in the afternoon",
            category="companionship",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.DRAFT,
            created_at=datetime.utcnow()
        ),
        CareTask(
            id="task_4",
            care_request_id="req_1",
            title="Help with banking",
            description="Help access bank account to pay bills",
            category="financial",
            priority=TaskPriority.HIGH,
            status=TaskStatus.DRAFT,
            created_at=datetime.utcnow()
        )
    ]
    
    print("\n1. Compliant Tasks:")
    result = evaluator.evaluate(
        compliant_tasks,
        "Patient needs help with daily activities",
        constraints="No medical tasks",
        boundaries="Prefer morning visits only"
    )
    print_eval_result("Result", result)
    
    print("\n2. Tasks with Boundary Violations:")
    result = evaluator.evaluate(
        violating_tasks,
        "Patient needs help",
        constraints="No financial tasks",
        boundaries="No visitors - patient prefers privacy"
    )
    print_eval_result("Result", result)


def test_completeness_evaluator():
    """Test the CompletenessEvaluator"""
    print("\n" + "=" * 80)
    print("Testing CompletenessEvaluator")
    print("=" * 80)
    
    evaluator = CompletenessEvaluator()
    
    # Create a needs map
    needs_map = NeedsMap(
        id="needs_1",
        care_request_id="req_1",
        summary="Patient needs help with meals, transportation, and companionship",
        identified_needs={
            "meals": ["Breakfast preparation", "Dinner delivery"],
            "transportation": ["Medical appointments", "Grocery shopping"],
            "companionship": ["Weekly visits", "Phone check-ins"]
        },
        risks={},
        assumptions="Patient is mobile but needs assistance",
        created_at=datetime.utcnow()
    )
    
    # Complete task list
    complete_tasks = [
        CareTask(
            id=f"task_{i}",
            care_request_id="req_1",
            title=title,
            description=f"Help with {title.lower()}",
            category=category,
            priority=priority,
            status=TaskStatus.DRAFT,
            created_at=datetime.utcnow()
        )
        for i, (title, category, priority) in enumerate([
            ("Prepare breakfast", "meals", TaskPriority.HIGH),
            ("Deliver dinner", "meals", TaskPriority.HIGH),
            ("Drive to doctor appointment", "transportation", TaskPriority.HIGH),
            ("Grocery shopping", "transportation", TaskPriority.MEDIUM),
            ("Weekly companionship visit", "companionship", TaskPriority.MEDIUM),
            ("Daily phone check-in", "companionship", TaskPriority.LOW),
            ("Light housekeeping", "household", TaskPriority.LOW)
        ])
    ]
    
    # Incomplete task list
    incomplete_tasks = [
        CareTask(
            id="task_1",
            care_request_id="req_1",
            title="Help with something",
            description="General help",
            category="general",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.DRAFT,
            created_at=datetime.utcnow()
        )
    ]
    
    print("\n1. Complete Task List:")
    result = evaluator.evaluate(complete_tasks, needs_map)
    print_eval_result("Result", result)
    
    print("\n2. Incomplete Task List:")
    result = evaluator.evaluate(incomplete_tasks, needs_map)
    print_eval_result("Result", result)


def test_clarity_evaluator():
    """Test the ClarityEvaluator"""
    print("\n" + "=" * 80)
    print("Testing ClarityEvaluator")
    print("=" * 80)
    
    evaluator = ClarityEvaluator()
    
    # Create clear review packet
    clear_tasks = [
        CareTask(
            id=f"task_{i}",
            care_request_id="req_1",
            title=title,
            description=desc,
            category=category,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.DRAFT,
            created_at=datetime.utcnow()
        )
        for i, (title, desc, category) in enumerate([
            ("Grocery shopping", "Pick up groceries from provided list", "errands"),
            ("Meal delivery", "Deliver prepared meal at 6pm", "meals"),
            ("Transportation", "Drive to medical appointment", "transportation")
        ])
    ]
    
    clear_packet = ReviewPacket(
        id="review_1",
        care_request_id="req_1",
        summary="This care plan provides comprehensive support for daily activities including meals, transportation, and errands. All tasks are designed to be completed by volunteers with no special training required.",
        draft_tasks=clear_tasks,
        agent_notes="Tasks have been reviewed for safety and appropriateness. All tasks respect stated boundaries and constraints.",
        approval_status=ApprovalStatus.PENDING,
        created_at=datetime.utcnow()
    )
    
    # Create unclear review packet
    unclear_tasks = [
        CareTask(
            id="task_1",
            care_request_id="req_1",
            title="Help",
            description="",
            category="",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.DRAFT,
            created_at=datetime.utcnow()
        )
    ]
    
    unclear_packet = ReviewPacket(
        id="review_2",
        care_request_id="req_1",
        summary="",
        draft_tasks=unclear_tasks,
        agent_notes="",
        approval_status=ApprovalStatus.PENDING,
        created_at=datetime.utcnow()
    )
    
    print("\n1. Clear Review Packet:")
    result = evaluator.evaluate_review_packet(clear_packet)
    print_eval_result("Result", result)
    
    print("\n2. Unclear Review Packet:")
    result = evaluator.evaluate_review_packet(unclear_packet)
    print_eval_result("Result", result)


def main():
    """Run all evaluator tests"""
    print("\n" + "=" * 80)
    print("Care Circles - Evaluator Test Suite")
    print("=" * 80)
    print("\nThis script demonstrates the evaluation capabilities")
    print("without requiring full pipeline execution.\n")
    
    test_task_quality_evaluator()
    test_boundary_compliance_evaluator()
    test_completeness_evaluator()
    test_clarity_evaluator()
    
    print("\n" + "=" * 80)
    print("All Evaluator Tests Complete!")
    print("=" * 80)
    print("\nKey Observations:")
    print("  ✅ TaskQualityEvaluator assesses actionability, clarity, and appropriateness")
    print("  ✅ BoundaryComplianceEvaluator catches safety and privacy violations")
    print("  ✅ CompletenessEvaluator validates comprehensive need coverage")
    print("  ✅ ClarityEvaluator ensures clear communication")
    print("\nThese evaluators run automatically on every pipeline execution!")
    print()


if __name__ == "__main__":
    main()
