"""
Agent orchestrator service

Coordinates the sequential execution of the 5-agent CrewAI pipeline (A1-A5).
Each agent processes the output of the previous agent to produce a complete care plan.
"""

import json
import logging
import re
from datetime import datetime
from typing import List, Dict, Any
from uuid import uuid4

from app.models.domain import CareRequest, NeedsMap, CareTask, ReviewPacket
from app.agents.crew_factory import CrewFactory
from app.agents.output_handlers import OutputHandler
from app.config.constants import AgentNames, TaskNames, TaskPriority, TaskStatus, ApprovalStatus

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates the sequential execution of the AI agent pipeline.
    
    Pipeline stages:
    A1: Intake & Needs Analysis → NeedsMap
    A2: Task Generation → List[CareTask]
    A3: Guardian & Quality Pass → Revised List[CareTask]
    A4: Optimization → Optimized List[CareTask]
    A5: Review Packet Assembly → ReviewPacket
    """
    
    def __init__(self):
        """Initialize the orchestrator with CrewFactory and OutputHandler"""
        self.crew_factory = CrewFactory()
        self.output_handler = OutputHandler()
        logger.info("AgentOrchestrator initialized")
    
    def run_pipeline_sync(self, care_request: CareRequest, progress_callback=None) -> ReviewPacket:
        """
        Execute the complete 5-agent pipeline synchronously (for thread pool execution).
        
        Args:
            care_request: The care request to process
            progress_callback: Optional callback function(agent_name, status) for progress updates
            
        Returns:
            ReviewPacket: The final review packet ready for human approval
        """
        start_time = datetime.utcnow()
        logger.info(f"Starting agent pipeline for care request: {care_request.id}")
        
        try:
            # A1: Intake & Needs Analysis
            if progress_callback:
                progress_callback("A1", "running")
            needs_map = self._run_agent_a1_sync(care_request)
            if progress_callback:
                progress_callback("A1", "completed")
            
            # A2: Task Generation
            if progress_callback:
                progress_callback("A2", "running")
            draft_tasks = self._run_agent_a2_sync(needs_map, care_request)
            if progress_callback:
                progress_callback("A2", "completed")
            
            # A3: Guardian & Quality Pass
            if progress_callback:
                progress_callback("A3", "running")
            reviewed_tasks = self._run_agent_a3_sync(draft_tasks, care_request)
            if progress_callback:
                progress_callback("A3", "completed")
            
            # A4: Optimization
            if progress_callback:
                progress_callback("A4", "running")
            optimized_tasks = self._run_agent_a4_sync(reviewed_tasks, care_request)
            if progress_callback:
                progress_callback("A4", "completed")
            
            # A5: Review Packet Assembly
            if progress_callback:
                progress_callback("A5", "running")
            review_packet = self._run_agent_a5_sync(optimized_tasks, needs_map, care_request)
            if progress_callback:
                progress_callback("A5", "completed")
            
            # Print pipeline summary
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.output_handler.print_pipeline_summary(
                care_request_id=care_request.id,
                total_tasks=len(review_packet.draft_tasks),
                execution_time=execution_time
            )
            
            logger.info(f"Pipeline completed for {care_request.id} in {execution_time:.2f}s")
            return review_packet
            
        except Exception as e:
            logger.error(f"Pipeline failed for {care_request.id}: {str(e)}", exc_info=True)
            self.output_handler.print_error("Pipeline Execution", e)
            raise
    
    def _run_agent_a1_sync(self, care_request: CareRequest) -> NeedsMap:
        """Synchronous version of A1"""
        logger.info("Executing A1: Intake & Needs Analysis")
        
        input_data = f"""
Care Request ID: {care_request.id}

NARRATIVE:
{care_request.narrative}

CONSTRAINTS:
{care_request.constraints or "None specified"}

BOUNDARIES:
{care_request.boundaries or "None specified"}
"""
        
        crew = self.crew_factory.create_single_agent_crew(
            agent_name=AgentNames.INTAKE_ANALYST,
            task_name=TaskNames.ANALYZE_NEEDS,
            input_data=input_data
        )
        
        result = crew.kickoff()
        needs_map = self._parse_needs_map(result, care_request.id)
        self.output_handler.print_needs_map(needs_map)
        
        return needs_map
    
    def _run_agent_a2_sync(self, needs_map: NeedsMap, care_request: CareRequest) -> List[CareTask]:
        """Synchronous version of A2"""
        logger.info("Executing A2: Task Generation")
        
        input_data = f"""
NeedsMap ID: {needs_map.id}

SUMMARY:
{needs_map.summary}

IDENTIFIED NEEDS:
{json.dumps(needs_map.identified_needs, indent=2)}

RISKS:
{json.dumps(needs_map.risks, indent=2)}

ASSUMPTIONS:
{needs_map.assumptions}

Care Request ID: {care_request.id}
"""
        
        crew = self.crew_factory.create_single_agent_crew(
            agent_name=AgentNames.TASK_GENERATOR,
            task_name=TaskNames.GENERATE_TASKS,
            input_data=input_data
        )
        
        result = crew.kickoff()
        tasks = self._parse_tasks(result, care_request)
        self.output_handler.print_tasks(tasks, "A2 - Task Generation", "Care Task Coordinator")
        
        return tasks
    
    def _run_agent_a3_sync(self, draft_tasks: List[CareTask], care_request: CareRequest) -> List[CareTask]:
        """Synchronous version of A3"""
        logger.info("Executing A3: Guardian & Quality Pass")
        
        tasks_data = []
        for task in draft_tasks:
            tasks_data.append({
                "title": task.title,
                "description": task.description,
                "category": task.category,
                "priority": task.priority
            })
        
        input_data = f"""
Draft Tasks to Review ({len(draft_tasks)} tasks):
{json.dumps(tasks_data, indent=2)}

Original Care Request Context:
- Narrative: {care_request.narrative[:200]}...
- Constraints: {care_request.constraints or "None"}
- Boundaries: {care_request.boundaries or "None"}
"""
        
        crew = self.crew_factory.create_single_agent_crew(
            agent_name=AgentNames.GUARDIAN_REVIEWER,
            task_name=TaskNames.REVIEW_QUALITY,
            input_data=input_data
        )
        
        result = crew.kickoff()
        reviewed_tasks = self._parse_reviewed_tasks(result, draft_tasks, care_request)
        self.output_handler.print_tasks(reviewed_tasks, "A3 - Guardian & Quality Pass", "Care Quality Guardian")
        
        return reviewed_tasks
    
    def _run_agent_a4_sync(self, reviewed_tasks: List[CareTask], care_request: CareRequest) -> List[CareTask]:
        """Synchronous version of A4"""
        logger.info("Executing A4: Optimization")
        
        tasks_data = []
        for task in reviewed_tasks:
            tasks_data.append({
                "title": task.title,
                "description": task.description,
                "category": task.category,
                "priority": task.priority
            })
        
        input_data = f"""
Tasks to Optimize ({len(reviewed_tasks)} tasks):
{json.dumps(tasks_data, indent=2)}

Optimization Goals:
- Remove duplicates
- Fill gaps in coverage
- Improve clarity
- Ensure logical organization
"""
        
        crew = self.crew_factory.create_single_agent_crew(
            agent_name=AgentNames.OPTIMIZATION_SPECIALIST,
            task_name=TaskNames.OPTIMIZE_PLAN,
            input_data=input_data
        )
        
        result = crew.kickoff()
        optimized_tasks = self._parse_optimized_tasks(result, reviewed_tasks, care_request)
        self.output_handler.print_tasks(optimized_tasks, "A4 - Optimization", "Care Plan Optimizer")
        
        return optimized_tasks
    
    def _run_agent_a5_sync(
        self,
        optimized_tasks: List[CareTask],
        needs_map: NeedsMap,
        care_request: CareRequest
    ) -> ReviewPacket:
        """Synchronous version of A5"""
        logger.info("Executing A5: Review Packet Assembly")
        
        tasks_data = []
        for task in optimized_tasks:
            tasks_data.append({
                "title": task.title,
                "description": task.description,
                "category": task.category,
                "priority": task.priority
            })
        
        input_data = f"""
Finalized Tasks ({len(optimized_tasks)} tasks):
{json.dumps(tasks_data, indent=2)}

Original Needs Analysis:
{needs_map.summary}

Care Request ID: {care_request.id}

Create a comprehensive review packet for the organizer.
"""
        
        crew = self.crew_factory.create_single_agent_crew(
            agent_name=AgentNames.REVIEW_ASSEMBLER,
            task_name=TaskNames.ASSEMBLE_REVIEW,
            input_data=input_data
        )
        
        result = crew.kickoff()
        review_packet = self._parse_review_packet(result, optimized_tasks, care_request.id)
        self.output_handler.print_review_packet(review_packet)
        
        return review_packet

    async def run_pipeline(self, care_request: CareRequest, progress_callback=None) -> ReviewPacket:
        """
        Execute the complete 5-agent pipeline.
        
        Args:
            care_request: The care request to process
            progress_callback: Optional callback function(agent_name, status) for progress updates
            
        Returns:
            ReviewPacket: The final review packet ready for human approval
        """
        start_time = datetime.utcnow()
        logger.info(f"Starting agent pipeline for care request: {care_request.id}")
        
        try:
            # A1: Intake & Needs Analysis
            if progress_callback:
                progress_callback("A1", "running")
            needs_map = await self._run_agent_a1(care_request)
            if progress_callback:
                progress_callback("A1", "completed")
            
            # A2: Task Generation
            if progress_callback:
                progress_callback("A2", "running")
            draft_tasks = await self._run_agent_a2(needs_map, care_request)
            if progress_callback:
                progress_callback("A2", "completed")
            
            # A3: Guardian & Quality Pass
            if progress_callback:
                progress_callback("A3", "running")
            reviewed_tasks = await self._run_agent_a3(draft_tasks, care_request)
            if progress_callback:
                progress_callback("A3", "completed")
            
            # A4: Optimization
            if progress_callback:
                progress_callback("A4", "running")
            optimized_tasks = await self._run_agent_a4(reviewed_tasks, care_request)
            if progress_callback:
                progress_callback("A4", "completed")
            
            # A5: Review Packet Assembly
            if progress_callback:
                progress_callback("A5", "running")
            review_packet = await self._run_agent_a5(optimized_tasks, needs_map, care_request)
            if progress_callback:
                progress_callback("A5", "completed")
            
            # Print pipeline summary
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.output_handler.print_pipeline_summary(
                care_request_id=care_request.id,
                total_tasks=len(review_packet.draft_tasks),
                execution_time=execution_time
            )
            
            logger.info(f"Pipeline completed for {care_request.id} in {execution_time:.2f}s")
            return review_packet
            
        except Exception as e:
            logger.error(f"Pipeline failed for {care_request.id}: {str(e)}", exc_info=True)
            self.output_handler.print_error("Pipeline Execution", e)
            raise
    
    async def _run_agent_a1(self, care_request: CareRequest) -> NeedsMap:
        """
        A1: Intake & Needs Analysis
        
        Analyzes the care request narrative and produces a structured needs map.
        """
        logger.info("Executing A1: Intake & Needs Analysis")
        
        # Prepare input data
        input_data = f"""
Care Request ID: {care_request.id}

NARRATIVE:
{care_request.narrative}

CONSTRAINTS:
{care_request.constraints or "None specified"}

BOUNDARIES:
{care_request.boundaries or "None specified"}
"""
        
        # Create and execute crew
        crew = self.crew_factory.create_single_agent_crew(
            agent_name=AgentNames.INTAKE_ANALYST,
            task_name=TaskNames.ANALYZE_NEEDS,
            input_data=input_data
        )
        
        result = crew.kickoff()
        
        # Parse result and create NeedsMap
        needs_map = self._parse_needs_map(result, care_request.id)
        
        # Print formatted output
        self.output_handler.print_needs_map(needs_map)
        
        return needs_map
    
    async def _run_agent_a2(self, needs_map: NeedsMap, care_request: CareRequest) -> List[CareTask]:
        """
        A2: Task Generation
        
        Transforms the needs map into actionable care tasks.
        """
        logger.info("Executing A2: Task Generation")
        
        # Prepare input data
        input_data = f"""
NeedsMap ID: {needs_map.id}

SUMMARY:
{needs_map.summary}

IDENTIFIED NEEDS:
{json.dumps(needs_map.identified_needs, indent=2)}

RISKS:
{json.dumps(needs_map.risks, indent=2)}

ASSUMPTIONS:
{needs_map.assumptions}

Care Request ID: {care_request.id}
"""
        
        # Create and execute crew
        crew = self.crew_factory.create_single_agent_crew(
            agent_name=AgentNames.TASK_GENERATOR,
            task_name=TaskNames.GENERATE_TASKS,
            input_data=input_data
        )
        
        result = crew.kickoff()
        
        # Parse result and create tasks
        tasks = self._parse_tasks(result, care_request)
        
        # Print formatted output
        self.output_handler.print_tasks(tasks, "A2 - Task Generation", "Care Task Coordinator")
        
        return tasks
    
    async def _run_agent_a3(self, draft_tasks: List[CareTask], care_request: CareRequest) -> List[CareTask]:
        """
        A3: Guardian & Quality Pass
        
        Reviews tasks for safety, appropriateness, and boundary compliance.
        """
        logger.info("Executing A3: Guardian & Quality Pass")
        
        # Prepare input data
        tasks_data = []
        for task in draft_tasks:
            tasks_data.append({
                "title": task.title,
                "description": task.description,
                "category": task.category,
                "priority": task.priority
            })
        
        input_data = f"""
Draft Tasks to Review ({len(draft_tasks)} tasks):
{json.dumps(tasks_data, indent=2)}

Original Care Request Context:
- Narrative: {care_request.narrative[:200]}...
- Constraints: {care_request.constraints or "None"}
- Boundaries: {care_request.boundaries or "None"}
"""
        
        # Create and execute crew
        crew = self.crew_factory.create_single_agent_crew(
            agent_name=AgentNames.GUARDIAN_REVIEWER,
            task_name=TaskNames.REVIEW_QUALITY,
            input_data=input_data
        )
        
        result = crew.kickoff()
        
        # Parse result and update tasks
        reviewed_tasks = self._parse_reviewed_tasks(result, draft_tasks, care_request)
        
        # Print formatted output
        self.output_handler.print_tasks(reviewed_tasks, "A3 - Guardian & Quality Pass", "Care Quality Guardian")
        
        return reviewed_tasks
    
    async def _run_agent_a4(self, reviewed_tasks: List[CareTask], care_request: CareRequest) -> List[CareTask]:
        """
        A4: Optimization
        
        Optimizes the task list for clarity, completeness, and efficiency.
        """
        logger.info("Executing A4: Optimization")
        
        # Prepare input data
        tasks_data = []
        for task in reviewed_tasks:
            tasks_data.append({
                "title": task.title,
                "description": task.description,
                "category": task.category,
                "priority": task.priority
            })
        
        input_data = f"""
Tasks to Optimize ({len(reviewed_tasks)} tasks):
{json.dumps(tasks_data, indent=2)}

Optimization Goals:
- Remove duplicates
- Fill gaps in coverage
- Improve clarity
- Ensure logical organization
"""
        
        # Create and execute crew
        crew = self.crew_factory.create_single_agent_crew(
            agent_name=AgentNames.OPTIMIZATION_SPECIALIST,
            task_name=TaskNames.OPTIMIZE_PLAN,
            input_data=input_data
        )
        
        result = crew.kickoff()
        
        # Parse result and update tasks
        optimized_tasks = self._parse_optimized_tasks(result, reviewed_tasks, care_request)
        
        # Print formatted output
        self.output_handler.print_tasks(optimized_tasks, "A4 - Optimization", "Care Plan Optimizer")
        
        return optimized_tasks
    
    async def _run_agent_a5(
        self,
        optimized_tasks: List[CareTask],
        needs_map: NeedsMap,
        care_request: CareRequest
    ) -> ReviewPacket:
        """
        A5: Review Packet Assembly
        
        Creates a comprehensive review packet for human approval.
        """
        logger.info("Executing A5: Review Packet Assembly")
        
        # Prepare input data
        tasks_data = []
        for task in optimized_tasks:
            tasks_data.append({
                "title": task.title,
                "description": task.description,
                "category": task.category,
                "priority": task.priority
            })
        
        input_data = f"""
Finalized Tasks ({len(optimized_tasks)} tasks):
{json.dumps(tasks_data, indent=2)}

Original Needs Analysis:
{needs_map.summary}

Care Request ID: {care_request.id}

Create a comprehensive review packet for the organizer.
"""
        
        # Create and execute crew
        crew = self.crew_factory.create_single_agent_crew(
            agent_name=AgentNames.REVIEW_ASSEMBLER,
            task_name=TaskNames.ASSEMBLE_REVIEW,
            input_data=input_data
        )
        
        result = crew.kickoff()
        
        # Parse result and create review packet
        review_packet = self._parse_review_packet(result, optimized_tasks, care_request.id)
        
        # Print formatted output
        self.output_handler.print_review_packet(review_packet)
        
        return review_packet
    
    def _extract_json(self, text: str) -> Any:
        """
        Extract JSON from agent response.
        Tries pure JSON first, then JSON in markdown code blocks.
        Raises ValueError if no valid JSON found.
        
        Returns:
            Parsed JSON object (dict or list)
        """
        # Try to parse as pure JSON first
        text_stripped = text.strip()
        if text_stripped.startswith('{') or text_stripped.startswith('['):
            try:
                return json.loads(text_stripped)
            except json.JSONDecodeError:
                pass
        
        # Try to extract JSON from markdown code blocks
        json_patterns = [
            r'```json\s*(\{.*?\}|\[.*?\])\s*```',  # ```json ... ```
            r'```\s*(\{.*?\}|\[.*?\])\s*```',      # ``` ... ```
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue
        
        # If no JSON found, raise error
        raise ValueError(
            f"No valid JSON found in agent response. "
            f"Response must be valid JSON only. Got: {text[:200]}..."
        )
    
    def _parse_needs_map(self, result: Any, care_request_id: str) -> NeedsMap:
        """Parse CrewAI result into NeedsMap object - expects JSON only"""
        result_text = str(result)
        
        try:
            data = self._extract_json(result_text)
            
            # Validate structure
            if not isinstance(data, dict):
                raise ValueError(f"Expected JSON object, got {type(data).__name__}")
            
            needs_map = NeedsMap(
                id=f"needs_{uuid4().hex[:16]}",
                care_request_id=care_request_id,
                summary=data.get('summary', ''),
                identified_needs=data.get('identified_needs', {}),
                risks=data.get('risks', {}),
                assumptions=data.get('assumptions', ''),
                created_at=datetime.utcnow()
            )
            
            logger.info(f"Successfully parsed NeedsMap from JSON")
            return needs_map
            
        except (ValueError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse NeedsMap from agent response: {e}")
            logger.error(f"Response text: {result_text[:500]}")
            raise ValueError(
                f"Agent A1 (Intake & Needs Analysis) failed to return valid JSON. "
                f"Expected JSON object with 'summary', 'identified_needs', 'risks', and 'assumptions' fields. "
                f"Error: {str(e)}"
            ) from e
    
    def _parse_tasks(self, result: Any, care_request: CareRequest) -> List[CareTask]:
        """Parse CrewAI result into list of CareTask objects - expects JSON array only"""
        result_text = str(result)
        tasks = []
        
        try:
            data = self._extract_json(result_text)
            
            # Handle both array format and object with tasks field
            if isinstance(data, list):
                tasks_data = data
            elif isinstance(data, dict) and 'tasks' in data:
                tasks_data = data['tasks']
            else:
                raise ValueError(f"Expected JSON array or object with 'tasks' field, got {type(data).__name__}")
            
            if not isinstance(tasks_data, list):
                raise ValueError(f"Expected array of tasks, got {type(tasks_data).__name__}")
            
            if len(tasks_data) == 0:
                logger.warning("Agent returned empty task list")
                return []
            
            logger.info(f"Found {len(tasks_data)} tasks in JSON format")
            
            for task_data in tasks_data:
                if not isinstance(task_data, dict):
                    logger.warning(f"Skipping invalid task data: {task_data}")
                    continue
                
                if 'title' not in task_data:
                    logger.warning(f"Skipping task without title: {task_data}")
                    continue
                
                # Map priority text to enum
                priority_text = task_data.get('priority', 'medium').lower()
                if "high" in priority_text:
                    priority = TaskPriority.HIGH
                elif "low" in priority_text:
                    priority = TaskPriority.LOW
                else:
                    priority = TaskPriority.MEDIUM
                
                task = CareTask(
                    id=f"task_{uuid4().hex[:16]}",
                    care_request_id=care_request.id,
                    title=task_data.get('title', 'Untitled Task'),
                    description=task_data.get('description', ''),
                    category=task_data.get('category', 'general').lower(),
                    priority=priority,
                    status=TaskStatus.DRAFT,
                    created_at=datetime.utcnow()
                )
                tasks.append(task)
            
            if tasks:
                logger.info(f"Successfully parsed {len(tasks)} tasks from JSON")
                return tasks
            else:
                raise ValueError("No valid tasks found in JSON response")
                
        except (ValueError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse tasks from agent response: {e}")
            logger.error(f"Response text: {result_text[:500]}")
            raise ValueError(
                f"Agent A2 (Task Generation) failed to return valid JSON. "
                f"Expected JSON array of task objects with 'title', 'description', 'category', and 'priority' fields. "
                f"Error: {str(e)}"
            ) from e
    
    def _parse_reviewed_tasks(
        self,
        result: Any,
        draft_tasks: List[CareTask],
        care_request: CareRequest
    ) -> List[CareTask]:
        """Parse reviewed tasks from A3 - expects JSON object with 'tasks' array"""
        result_text = str(result)
        
        try:
            data = self._extract_json(result_text)
            
            if not isinstance(data, dict):
                raise ValueError(f"Expected JSON object with 'tasks' field, got {type(data).__name__}")
            
            if 'tasks' not in data:
                raise ValueError("JSON object missing required 'tasks' field")
            
            tasks_data = data['tasks']
            if not isinstance(tasks_data, list):
                raise ValueError(f"Expected 'tasks' to be an array, got {type(tasks_data).__name__}")
            
            logger.info(f"Guardian provided {len(tasks_data)} revised tasks in JSON")
            reviewed_tasks = []
            
            for task_data in tasks_data:
                if not isinstance(task_data, dict):
                    logger.warning(f"Skipping invalid task data: {task_data}")
                    continue
                
                if 'title' not in task_data:
                    logger.warning(f"Skipping task without title: {task_data}")
                    continue
                
                priority_text = task_data.get('priority', 'medium').lower()
                if "high" in priority_text:
                    priority = TaskPriority.HIGH
                elif "low" in priority_text:
                    priority = TaskPriority.LOW
                else:
                    priority = TaskPriority.MEDIUM
                
                # Try to match with existing task to preserve ID
                title = task_data.get('title', '')
                existing_task = next((t for t in draft_tasks if t.title.lower() == title.lower()), None)
                task_id = existing_task.id if existing_task else f"task_{uuid4().hex[:16]}"
                
                task = CareTask(
                    id=task_id,
                    care_request_id=care_request.id,
                    title=title,
                    description=task_data.get('description', ''),
                    category=task_data.get('category', 'general').lower(),
                    priority=priority,
                    status=TaskStatus.DRAFT,
                    created_at=datetime.utcnow()
                )
                reviewed_tasks.append(task)
            
            if reviewed_tasks:
                logger.info(f"Successfully parsed {len(reviewed_tasks)} reviewed tasks from JSON")
                return reviewed_tasks
            else:
                raise ValueError("No valid tasks found in JSON response")
                
        except (ValueError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse reviewed tasks from agent response: {e}")
            logger.error(f"Response text: {result_text[:500]}")
            raise ValueError(
                f"Agent A3 (Guardian & Quality Pass) failed to return valid JSON. "
                f"Expected JSON object with 'tasks' array and optional 'review_notes' field. "
                f"Error: {str(e)}"
            ) from e
    
    def _parse_optimized_tasks(
        self,
        result: Any,
        reviewed_tasks: List[CareTask],
        care_request: CareRequest
    ) -> List[CareTask]:
        """Parse optimized tasks from A4 - expects JSON object with 'tasks' array"""
        result_text = str(result)
        
        try:
            data = self._extract_json(result_text)
            
            if not isinstance(data, dict):
                raise ValueError(f"Expected JSON object with 'tasks' field, got {type(data).__name__}")
            
            if 'tasks' not in data:
                raise ValueError("JSON object missing required 'tasks' field")
            
            tasks_data = data['tasks']
            if not isinstance(tasks_data, list):
                raise ValueError(f"Expected 'tasks' to be an array, got {type(tasks_data).__name__}")
            
            logger.info(f"Optimizer provided {len(tasks_data)} optimized tasks in JSON")
            optimized_tasks = []
            
            for task_data in tasks_data:
                if not isinstance(task_data, dict):
                    logger.warning(f"Skipping invalid task data: {task_data}")
                    continue
                
                if 'title' not in task_data:
                    logger.warning(f"Skipping task without title: {task_data}")
                    continue
                
                priority_text = task_data.get('priority', 'medium').lower()
                if "high" in priority_text:
                    priority = TaskPriority.HIGH
                elif "low" in priority_text:
                    priority = TaskPriority.LOW
                else:
                    priority = TaskPriority.MEDIUM
                
                # Try to match with existing task to preserve ID
                title = task_data.get('title', '')
                existing_task = next((t for t in reviewed_tasks if t.title.lower() == title.lower()), None)
                task_id = existing_task.id if existing_task else f"task_{uuid4().hex[:16]}"
                
                task = CareTask(
                    id=task_id,
                    care_request_id=care_request.id,
                    title=title,
                    description=task_data.get('description', ''),
                    category=task_data.get('category', 'general').lower(),
                    priority=priority,
                    status=TaskStatus.DRAFT,
                    created_at=datetime.utcnow()
                )
                optimized_tasks.append(task)
            
            if optimized_tasks:
                logger.info(f"Successfully parsed {len(optimized_tasks)} optimized tasks from JSON")
                return optimized_tasks
            else:
                raise ValueError("No valid tasks found in JSON response")
                
        except (ValueError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse optimized tasks from agent response: {e}")
            logger.error(f"Response text: {result_text[:500]}")
            raise ValueError(
                f"Agent A4 (Optimization) failed to return valid JSON. "
                f"Expected JSON object with 'tasks' array and optional 'optimization_notes' field. "
                f"Error: {str(e)}"
            ) from e
    
    def _parse_review_packet(
        self,
        result: Any,
        optimized_tasks: List[CareTask],
        care_request_id: str
    ) -> ReviewPacket:
        """Parse final review packet from A5 - expects JSON object"""
        result_text = str(result)
        
        try:
            data = self._extract_json(result_text)
            
            if not isinstance(data, dict):
                raise ValueError(f"Expected JSON object, got {type(data).__name__}")
            
            # Extract tasks from the response or use provided optimized_tasks
            if 'draft_tasks' in data and isinstance(data['draft_tasks'], list):
                # Parse tasks from response
                tasks_data = data['draft_tasks']
                parsed_tasks = []
                
                for task_data in tasks_data:
                    if not isinstance(task_data, dict) or 'title' not in task_data:
                        continue
                    
                    priority_text = task_data.get('priority', 'medium').lower()
                    if "high" in priority_text:
                        priority = TaskPriority.HIGH
                    elif "low" in priority_text:
                        priority = TaskPriority.LOW
                    else:
                        priority = TaskPriority.MEDIUM
                    
                    # Try to match with existing task to preserve ID
                    title = task_data.get('title', '')
                    existing_task = next((t for t in optimized_tasks if t.title.lower() == title.lower()), None)
                    task_id = existing_task.id if existing_task else f"task_{uuid4().hex[:16]}"
                    
                    task = CareTask(
                        id=task_id,
                        care_request_id=care_request_id,
                        title=title,
                        description=task_data.get('description', ''),
                        category=task_data.get('category', 'general').lower(),
                        priority=priority,
                        status=TaskStatus.DRAFT,
                        created_at=datetime.utcnow()
                    )
                    parsed_tasks.append(task)
                
                final_tasks = parsed_tasks if parsed_tasks else optimized_tasks
            else:
                # Use provided optimized_tasks if not in response
                final_tasks = optimized_tasks
            
            suggested = (data.get('suggested_plan_name') or '').strip()
            review_packet = ReviewPacket(
                id=f"review_{uuid4().hex[:16]}",
                care_request_id=care_request_id,
                suggested_plan_name=suggested if suggested else None,
                summary=data.get('summary', ''),
                draft_tasks=final_tasks,
                agent_notes=data.get('agent_notes', ''),
                approval_status=ApprovalStatus.PENDING,
                created_at=datetime.utcnow()
            )
            
            logger.info(f"Successfully parsed ReviewPacket from JSON")
            return review_packet
            
        except (ValueError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse review packet from agent response: {e}")
            logger.error(f"Response text: {result_text[:500]}")
            raise ValueError(
                f"Agent A5 (Review Packet Assembly) failed to return valid JSON. "
                f"Expected JSON object with 'summary', 'draft_tasks', 'agent_notes', and 'approval_status' fields. "
                f"Error: {str(e)}"
            ) from e
