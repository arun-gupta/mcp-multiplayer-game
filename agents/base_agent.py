"""
Custom Agent Base Class
Simple replacement for crewai.Agent to eliminate heavy dependencies
"""
from typing import Optional, Any
from langchain_core.language_models import BaseLanguageModel

class Agent:
    """Simple Agent class to replace crewai.Agent"""
    
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        verbose: bool = True,
        allow_delegation: bool = False,
        llm: Optional[BaseLanguageModel] = None
    ):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose
        self.allow_delegation = allow_delegation
        self.llm = llm
    
    def execute(self, task: str) -> str:
        """Execute a task using the agent's LLM"""
        if self.llm is None:
            return f"Agent {self.role} cannot execute task: No LLM available"
        
        # Simple task execution
        prompt = f"""
Role: {self.role}
Goal: {self.goal}
Backstory: {self.backstory}

Task: {task}

Please provide a response based on your role and goal.
"""
        
        try:
            response = self.llm.invoke(prompt)
            return str(response)
        except Exception as e:
            return f"Error executing task: {str(e)}"
