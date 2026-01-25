"""
Console output handlers for pretty-printing agent results

Provides formatted, colorized console output for each stage of the agent pipeline.
This allows easy evaluation of agent outputs before database persistence is added.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
from colorama import Fore, Style, init

from app.models.domain import NeedsMap, CareTask, ReviewPacket

# Initialize colorama for cross-platform color support
init(autoreset=True)

logger = logging.getLogger(__name__)


class OutputHandler:
    """
    Handles formatted console output for agent pipeline stages
    """
    
    @staticmethod
    def print_separator(title: str = "", width: int = 80) -> None:
        """Print a visual separator with optional title"""
        if title:
            print(f"\n{Fore.CYAN}{'=' * width}")
            print(f"{Fore.CYAN}{title.center(width)}")
            print(f"{Fore.CYAN}{'=' * width}{Style.RESET_ALL}\n")
        else:
            print(f"{Fore.CYAN}{'=' * width}{Style.RESET_ALL}")
    
    @staticmethod
    def print_stage_header(stage: str, agent_name: str) -> None:
        """Print a header for an agent pipeline stage"""
        OutputHandler.print_separator(f"AGENT PIPELINE: {stage}", 80)
        print(f"{Fore.GREEN}Agent:{Style.RESET_ALL} {agent_name}")
        print(f"{Fore.GREEN}Started:{Style.RESET_ALL} {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    
    @staticmethod
    def print_stage_footer(success: bool = True) -> None:
        """Print a footer for an agent pipeline stage"""
        if success:
            print(f"\n{Fore.GREEN}✓ Stage Complete{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}✗ Stage Failed{Style.RESET_ALL}")
        OutputHandler.print_separator()
    
    @staticmethod
    def print_needs_map(needs_map: NeedsMap) -> None:
        """
        Pretty-print a NeedsMap from A1 (Intake & Needs Analysis)
        
        Args:
            needs_map: The NeedsMap to display
        """
        OutputHandler.print_stage_header("A1 - Intake & Needs Analysis", "Care Needs Analyst")
        
        print(f"{Fore.YELLOW}Summary:{Style.RESET_ALL}")
        print(f"  {needs_map.summary}\n")
        
        print(f"{Fore.YELLOW}Identified Needs:{Style.RESET_ALL}")
        for category, needs in needs_map.identified_needs.items():
            print(f"  {Fore.MAGENTA}{category}:{Style.RESET_ALL}")
            if isinstance(needs, list):
                for need in needs:
                    print(f"    • {need}")
            else:
                print(f"    • {needs}")
        
        print(f"\n{Fore.YELLOW}Risks & Concerns:{Style.RESET_ALL}")
        for risk_type, description in needs_map.risks.items():
            print(f"  {Fore.RED}⚠{Style.RESET_ALL} {risk_type}: {description}")
        
        print(f"\n{Fore.YELLOW}Assumptions:{Style.RESET_ALL}")
        print(f"  {needs_map.assumptions}")
        
        OutputHandler.print_stage_footer()
    
    @staticmethod
    def print_tasks(tasks: List[CareTask], stage_name: str, agent_name: str) -> None:
        """
        Pretty-print a list of CareTask objects
        
        Args:
            tasks: List of tasks to display
            stage_name: Name of the pipeline stage
            agent_name: Name of the agent that produced these tasks
        """
        OutputHandler.print_stage_header(stage_name, agent_name)
        
        print(f"{Fore.YELLOW}Generated {len(tasks)} tasks:{Style.RESET_ALL}\n")
        
        # Group by priority
        high_priority = [t for t in tasks if t.priority == "high"]
        medium_priority = [t for t in tasks if t.priority == "medium"]
        low_priority = [t for t in tasks if t.priority == "low"]
        
        for priority_group, priority_name, color in [
            (high_priority, "HIGH PRIORITY", Fore.RED),
            (medium_priority, "MEDIUM PRIORITY", Fore.YELLOW),
            (low_priority, "LOW PRIORITY", Fore.CYAN)
        ]:
            if priority_group:
                print(f"{color}━━ {priority_name} ({len(priority_group)} tasks) ━━{Style.RESET_ALL}")
                for task in priority_group:
                    print(f"\n  {Fore.GREEN}▸ {task.title}{Style.RESET_ALL}")
                    print(f"    Category: {task.category}")
                    print(f"    Description: {task.description[:150]}{'...' if len(task.description) > 150 else ''}")
                print()
        
        OutputHandler.print_stage_footer()
    
    @staticmethod
    def print_review_notes(notes: str, stage_name: str) -> None:
        """
        Print agent notes or review comments
        
        Args:
            notes: The notes to display
            stage_name: Name of the pipeline stage
        """
        print(f"\n{Fore.YELLOW}Agent Notes ({stage_name}):{Style.RESET_ALL}")
        print(f"  {notes}\n")
    
    @staticmethod
    def print_review_packet(packet: ReviewPacket) -> None:
        """
        Pretty-print a ReviewPacket from A5 (Review Packet Assembly)
        
        Args:
            packet: The ReviewPacket to display
        """
        OutputHandler.print_stage_header("A5 - Review Packet Assembly", "Care Plan Presenter")
        
        print(f"{Fore.YELLOW}Executive Summary:{Style.RESET_ALL}")
        print(f"  {packet.summary}\n")
        
        print(f"{Fore.YELLOW}Care Plan - {len(packet.draft_tasks)} Tasks Generated:{Style.RESET_ALL}\n")
        
        # Group by category
        tasks_by_category: Dict[str, List[CareTask]] = {}
        for task in packet.draft_tasks:
            category = task.category
            if category not in tasks_by_category:
                tasks_by_category[category] = []
            tasks_by_category[category].append(task)
        
        for category, tasks in tasks_by_category.items():
            print(f"{Fore.MAGENTA}━━ {category.upper()} ({len(tasks)} tasks) ━━{Style.RESET_ALL}")
            for task in tasks:
                priority_color = {
                    "high": Fore.RED,
                    "medium": Fore.YELLOW,
                    "low": Fore.CYAN
                }.get(task.priority, Fore.WHITE)
                
                print(f"\n  {priority_color}[{task.priority.upper()}]{Style.RESET_ALL} {Fore.GREEN}{task.title}{Style.RESET_ALL}")
                print(f"    {task.description[:200]}{'...' if len(task.description) > 200 else ''}")
            print()
        
        print(f"{Fore.YELLOW}Agent Notes & Recommendations:{Style.RESET_ALL}")
        print(f"  {packet.agent_notes[:500]}{'...' if len(packet.agent_notes) > 500 else ''}\n")
        
        print(f"{Fore.YELLOW}Approval Status:{Style.RESET_ALL} {packet.approval_status}")
        print(f"{Fore.YELLOW}Review Packet ID:{Style.RESET_ALL} {packet.id}")
        
        OutputHandler.print_stage_footer()
    
    @staticmethod
    def print_pipeline_summary(
        care_request_id: str,
        total_tasks: int,
        execution_time: float
    ) -> None:
        """
        Print a summary of the entire pipeline execution
        
        Args:
            care_request_id: ID of the processed care request
            total_tasks: Total number of tasks generated
            execution_time: Time taken to execute pipeline (seconds)
        """
        OutputHandler.print_separator("PIPELINE EXECUTION COMPLETE", 80)
        
        print(f"{Fore.GREEN}✓ All stages completed successfully{Style.RESET_ALL}\n")
        print(f"  Care Request ID: {care_request_id}")
        print(f"  Total Tasks Generated: {total_tasks}")
        print(f"  Execution Time: {execution_time:.2f} seconds")
        print(f"  Status: Ready for human review\n")
        
        OutputHandler.print_separator()
    
    @staticmethod
    def print_error(stage: str, error: Exception) -> None:
        """
        Print an error message for a failed stage
        
        Args:
            stage: Name of the stage that failed
            error: The exception that occurred
        """
        print(f"\n{Fore.RED}✗ ERROR in {stage}{Style.RESET_ALL}")
        print(f"{Fore.RED}  {type(error).__name__}: {str(error)}{Style.RESET_ALL}\n")
        OutputHandler.print_stage_footer(success=False)
