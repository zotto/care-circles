"""
Demo script for Care Circles Observability with Opik

This script demonstrates the observability and evaluation capabilities
by running sample care requests and displaying metrics.

Usage:
    python demo_observability.py
"""

import asyncio
import json
import logging
from datetime import datetime
from uuid import uuid4

from app.models.domain import CareRequest
from app.config.constants import RequestStatus
from app.observability.instrumented_orchestrator import InstrumentedOrchestrator
from app.observability.metrics import metrics_collector
from app.observability.opik_client import opik_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Sample care requests for demonstration
SAMPLE_REQUESTS = [
    {
        "narrative": """
        My elderly mother (78) recently had hip replacement surgery and is recovering at home.
        She lives alone and needs help with daily activities while she regains mobility.
        She's independent and proud, so we need to be respectful of her autonomy.
        She needs help with grocery shopping, meal preparation, light housekeeping,
        and transportation to physical therapy appointments twice a week.
        """,
        "constraints": "No medical tasks - she has a home health nurse for that",
        "boundaries": "She prefers morning visits (9am-12pm) and doesn't want visitors on Sundays"
    },
    {
        "narrative": """
        Our family friend John (65) is undergoing chemotherapy treatment for cancer.
        His wife works full-time and they have no family nearby. He needs support
        during the day when she's at work. He gets tired easily and sometimes feels nauseous.
        He would appreciate companionship, help with light meals, and someone to drive him
        to appointments when his wife isn't available.
        """,
        "constraints": "Must respect his privacy and energy levels",
        "boundaries": "No visitors during treatment weeks (Monday-Wednesday)"
    },
    {
        "narrative": """
        My neighbor Sarah (55) broke her arm and can't drive for 6 weeks. She has two
        teenage kids who need rides to school and activities. She also needs help with
        grocery shopping and meal prep since she can't cook with one arm. She's very
        organized and has a detailed schedule for the kids' activities.
        """,
        "constraints": "Kids' safety is top priority - only trusted drivers",
        "boundaries": "Prefer help from people who have passed background checks"
    }
]


def print_banner(text: str):
    """Print a formatted banner"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_section(text: str):
    """Print a formatted section header"""
    print("\n" + "-" * 80)
    print(f"  {text}")
    print("-" * 80 + "\n")


async def run_demo():
    """Run the observability demo"""
    
    print_banner("Care Circles - Observability Demo with Opik")
    
    # Check if Opik is enabled
    if opik_client.is_enabled():
        print("✅ Opik observability is ENABLED")
        print(f"   Workspace: {opik_client.client._workspace if opik_client.client else 'N/A'}")
        print(f"   Project: care-circles-hackathon")
    else:
        print("⚠️  Opik observability is DISABLED")
        print("   Set OPIK_API_KEY in .env to enable full observability")
    
    print("\nThis demo will:")
    print("  1. Process 3 sample care requests")
    print("  2. Trace all agent executions in Opik")
    print("  3. Evaluate each care plan across 5 dimensions")
    print("  4. Display comprehensive metrics and statistics")
    print("\n")
    
    input("Press Enter to start the demo...")
    
    # Initialize orchestrator
    orchestrator = InstrumentedOrchestrator()
    
    # Process each sample request
    for idx, sample in enumerate(SAMPLE_REQUESTS, 1):
        print_section(f"Processing Care Request {idx}/{len(SAMPLE_REQUESTS)}")
        
        # Create care request
        care_request = CareRequest(
            id=f"demo_{uuid4().hex[:12]}",
            user_id="demo_user",
            narrative=sample["narrative"].strip(),
            constraints=sample["constraints"],
            boundaries=sample["boundaries"],
            status=RequestStatus.SUBMITTED,
            created_at=datetime.utcnow()
        )
        
        print(f"Care Request ID: {care_request.id}")
        print(f"Narrative: {care_request.narrative[:100]}...")
        print(f"\nProcessing with full observability...\n")
        
        try:
            # Run pipeline with experiment tracking
            start_time = datetime.utcnow()
            
            review_packet = orchestrator.run_pipeline_sync(
                care_request=care_request,
                experiment_name=f"demo_run_{idx}",
                experiment_params={
                    "model": "gpt-4",
                    "sample_id": idx,
                    "demo_mode": True
                }
            )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Display results
            print_section("Results")
            print(f"✅ Pipeline completed successfully in {duration:.2f}s")
            print(f"📋 Generated {len(review_packet.draft_tasks)} care tasks")
            print(f"📝 Review Packet ID: {review_packet.id}")
            
            # Show sample tasks
            print("\nSample Tasks Generated:")
            for i, task in enumerate(review_packet.draft_tasks[:3], 1):
                print(f"\n  {i}. {task.title}")
                print(f"     Category: {task.category} | Priority: {task.priority}")
                print(f"     {task.description[:80]}...")
            
            if len(review_packet.draft_tasks) > 3:
                print(f"\n  ... and {len(review_packet.draft_tasks) - 3} more tasks")
            
        except Exception as e:
            print(f"❌ Error processing request: {str(e)}")
            logger.error(f"Error in demo: {e}", exc_info=True)
        
        if idx < len(SAMPLE_REQUESTS):
            print("\n")
            input("Press Enter to continue to next request...")
    
    # Display comprehensive metrics
    print_banner("Comprehensive Metrics & Evaluation Results")
    
    report = metrics_collector.get_comprehensive_report()
    
    # Summary
    print_section("Summary")
    summary = report.get("summary", {})
    print(f"Total Pipelines Executed: {summary.get('total_pipelines', 0)}")
    print(f"Total Agent Executions: {summary.get('total_agent_executions', 0)}")
    print(f"Unique Agents: {summary.get('unique_agents', 0)}")
    
    # Pipeline Statistics
    print_section("Pipeline Statistics")
    pipeline_stats = report.get("pipeline_statistics", {})
    if pipeline_stats:
        print(f"Success Rate: {pipeline_stats.get('success_rate', 0) * 100:.1f}%")
        print(f"Average Duration: {pipeline_stats.get('avg_duration', 0):.2f}s")
        print(f"Min Duration: {pipeline_stats.get('min_duration', 0):.2f}s")
        print(f"Max Duration: {pipeline_stats.get('max_duration', 0):.2f}s")
        print(f"Average Tasks per Plan: {pipeline_stats.get('avg_task_count', 0):.1f}")
        print(f"Min Tasks: {pipeline_stats.get('min_task_count', 0)}")
        print(f"Max Tasks: {pipeline_stats.get('max_task_count', 0)}")
    else:
        print("No pipeline statistics available")
    
    # Agent Performance
    print_section("Agent Performance")
    agent_stats = report.get("agent_statistics", {})
    if agent_stats:
        for agent_name, stats in agent_stats.items():
            print(f"\n{agent_name}:")
            print(f"  Executions: {stats.get('execution_count', 0)}")
            print(f"  Success Rate: {stats.get('success_rate', 0) * 100:.1f}%")
            print(f"  Avg Duration: {stats.get('avg_duration', 0):.2f}s")
            print(f"  Total Duration: {stats.get('total_duration', 0):.2f}s")
    else:
        print("No agent statistics available")
    
    # Evaluation Scores
    print_section("Evaluation Scores")
    eval_summary = report.get("evaluation_summary", {})
    if eval_summary:
        for eval_name, eval_data in eval_summary.items():
            if isinstance(eval_data, dict):
                print(f"\n{eval_name.replace('_', ' ').title()}:")
                print(f"  Average: {eval_data.get('avg', 0):.3f}")
                print(f"  Min: {eval_data.get('min', 0):.3f}")
                print(f"  Max: {eval_data.get('max', 0):.3f}")
                print(f"  Samples: {eval_data.get('count', 0)}")
    else:
        print("No evaluation scores available")
    
    # Overall Quality Assessment
    print_section("Overall Quality Assessment")
    
    if eval_summary and "overall" in eval_summary:
        overall_score = eval_summary["overall"].get("avg", 0)
        print(f"Overall Quality Score: {overall_score:.3f}")
        
        if overall_score >= 0.85:
            print("✅ EXCELLENT - Production-ready quality")
        elif overall_score >= 0.75:
            print("✅ GOOD - High-quality care plans")
        elif overall_score >= 0.65:
            print("⚠️  FAIR - Acceptable but needs improvement")
        else:
            print("❌ NEEDS WORK - Quality below target")
    
    # Opik Dashboard Link
    print_section("View in Opik Dashboard")
    if opik_client.is_enabled():
        print("🔗 View detailed traces and metrics in your Opik dashboard:")
        print("   https://www.comet.com/opik")
        print("\n   Project: care-circles-hackathon")
        print("\n   You can see:")
        print("   • Full execution traces for each agent (A1-A5)")
        print("   • Input/output at each stage")
        print("   • Evaluation scores and metrics")
        print("   • Execution timelines and performance")
    else:
        print("⚠️  Opik is disabled. Set OPIK_API_KEY to view in dashboard.")
    
    # API Endpoints (optional; primary view is Opik dashboard)
    print_section("Optional API Endpoints")
    print("Metrics are best viewed in the Opik dashboard. Optional REST endpoints:")
    print("\n  GET /api/observability/metrics/summary")
    print("  GET /api/observability/metrics/agent/{agent_name}")
    print("  GET /api/observability/metrics/evaluations")
    
    print_banner("Demo Complete!")
    print("\nKey Takeaways:")
    print("  ✅ All agent executions are automatically traced")
    print("  ✅ Each care plan is evaluated across 5 dimensions")
    print("  ✅ Real-time metrics are collected and aggregated")
    print("  ✅ View traces and metrics in the Opik dashboard")
    print("  ✅ Full observability for production monitoring")
    print("\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
