"""
CrewAI factory for creating agents and crews

This module loads agent and task configurations from YAML files and
instantiates CrewAI Agent and Crew objects for the pipeline.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.config.constants import AgentNames, TaskNames

logger = logging.getLogger(__name__)


class CrewFactory:
    """
    Factory for creating CrewAI agents and crews from YAML configuration
    """
    
    def __init__(self):
        """Initialize the factory and load configurations"""
        self.config_dir = Path(__file__).parent / "config"
        self.agents_config = self._load_yaml("agents.yaml")
        self.tasks_config = self._load_yaml("tasks.yaml")
        self.llm = self._create_llm()
        logger.info("CrewFactory initialized with configurations")
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file
        
        Args:
            filename: Name of the YAML file in the config directory
            
        Returns:
            Dict containing the parsed YAML content
        """
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded configuration from {filename}")
        return config
    
    def _create_llm(self) -> ChatOpenAI:
        """
        Create the LLM instance for agents
        
        Returns:
            ChatOpenAI: Configured LLM instance
        """
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
        logger.info(f"Created LLM instance: {settings.OPENAI_MODEL}")
        return llm
    
    def create_agent(self, agent_name: str) -> Agent:
        """
        Create a CrewAI agent from configuration
        
        Args:
            agent_name: Name of the agent (from AgentNames constants)
            
        Returns:
            Agent: Configured CrewAI agent
        """
        if agent_name not in self.agents_config:
            raise ValueError(f"Agent configuration not found: {agent_name}")
        
        config = self.agents_config[agent_name]
        
        agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=self.llm,
            verbose=config.get("verbose", True),
            allow_delegation=config.get("allow_delegation", False)
        )
        
        logger.info(f"Created agent: {agent_name} ({config['role']})")
        return agent
    
    def create_task(self, task_name: str, agent: Agent, input_data: str) -> Task:
        """
        Create a CrewAI task from configuration
        
        Args:
            task_name: Name of the task (from TaskNames constants)
            agent: The agent assigned to this task
            input_data: Input data/context for the task
            
        Returns:
            Task: Configured CrewAI task
        """
        if task_name not in self.tasks_config:
            raise ValueError(f"Task configuration not found: {task_name}")
        
        config = self.tasks_config[task_name]
        
        # Combine task description with input data
        full_description = f"{config['description']}\n\nINPUT DATA:\n{input_data}"
        
        task = Task(
            description=full_description,
            expected_output=config["expected_output"],
            agent=agent
        )
        
        logger.info(f"Created task: {task_name}")
        return task
    
    def create_crew(self, agents: list[Agent], tasks: list[Task]) -> Crew:
        """
        Create a CrewAI crew with the given agents and tasks
        
        Args:
            agents: List of agents for the crew
            tasks: List of tasks for the crew
            
        Returns:
            Crew: Configured CrewAI crew
        """
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True
        )
        
        logger.info(f"Created crew with {len(agents)} agents and {len(tasks)} tasks")
        return crew
    
    def create_single_agent_crew(
        self,
        agent_name: str,
        task_name: str,
        input_data: str
    ) -> Crew:
        """
        Convenience method to create a crew with a single agent and task
        
        This is the primary method used by the orchestrator for sequential execution.
        
        Args:
            agent_name: Name of the agent
            task_name: Name of the task
            input_data: Input data for the task
            
        Returns:
            Crew: Single-agent crew ready to execute
        """
        agent = self.create_agent(agent_name)
        task = self.create_task(task_name, agent, input_data)
        crew = self.create_crew([agent], [task])
        
        logger.info(f"Created single-agent crew: {agent_name} / {task_name}")
        return crew
