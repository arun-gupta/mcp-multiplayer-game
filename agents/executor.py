"""
Executor MCP Agent Module
Executor agent with MCP capabilities for distributed communication
"""
from .base_mcp_agent import BaseMCPAgent
from crewai import Task
from typing import Dict, List
import asyncio
from datetime import datetime
from models.factory import ModelFactory


class ExecutorMCPAgent(BaseMCPAgent):
    """Executor agent with MCP capabilities"""
    
    def __init__(self, model_config: Dict):
        # Create LLM first
        llm = self.create_llm(model_config)
        
        super().__init__(
            role="Executor Agent",
            goal="Execute moves and validate game state",
            backstory="""You are precise and decisive. You execute the strategic plans
            and ensure all moves are valid and properly implemented.""",
            mcp_port=3003,
            agent_id="executor",
            llm=llm
        )
    
    def register_agent_specific_endpoints(self):
        """Register Executor-specific MCP endpoints"""
        self.register_handler("execute_move", self.execute_move)
        self.register_handler("validate_move", self.validate_move)
        self.register_handler("update_game_state", self.update_game_state)
        self.register_handler("confirm_execution", self.confirm_execution)
    
    async def execute_move(self, strategy_data: Dict) -> Dict:
        """Execute the strategic move"""
        try:
            recommended_move = strategy_data.get("recommended_move", {})
            reasoning = strategy_data.get("reasoning", "")
            
            # Create execution task
            execution_task = Task(
                description=f"""
                Execute this move: {recommended_move}
                Based on reasoning: {reasoning}
                
                Validate the move and confirm execution.
                """,
                expected_output="Move execution confirmation and result"
            )
            
            # Execute using CrewAI
            try:
                execution_result = await asyncio.to_thread(self.execute, execution_task)
            except AttributeError:
                execution_result = await asyncio.to_thread(self.llm.call, execution_task.description)
            
            return {
                "agent_id": "executor",
                "move_executed": recommended_move,
                "result": execution_result,
                "success": True,
                "game_state": "updated",  # TODO: Get actual game state
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "agent_id": "executor", "success": False}
    
    async def validate_move(self, move_data: Dict) -> Dict:
        """Validate if a move is legal and strategic"""
        validation_task = Task(
            description=f"Validate this move: {move_data}",
            expected_output="Move validation with legal and strategic assessment"
        )
        
        try:
            result = await asyncio.to_thread(self.execute, validation_task)
        except AttributeError:
            result = await asyncio.to_thread(self.llm.call, validation_task.description)
        
        return {
            "agent_id": "executor",
            "validation": result,
            "is_legal": True,  # Extract from result
            "is_strategic": True,  # Extract from result
            "timestamp": datetime.now().isoformat()
        }
    
    async def update_game_state(self, state_data: Dict) -> Dict:
        """Update the game state after move execution"""
        update_task = Task(
            description=f"Update game state with: {state_data}",
            expected_output="Updated game state confirmation"
        )
        
        try:
            result = await asyncio.to_thread(self.execute, update_task)
        except AttributeError:
            result = await asyncio.to_thread(self.llm.call, update_task.description)
        
        return {
            "agent_id": "executor",
            "state_update": result,
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
    
    async def confirm_execution(self, execution_data: Dict) -> Dict:
        """Confirm successful move execution"""
        confirmation_task = Task(
            description=f"Confirm execution of: {execution_data}",
            expected_output="Execution confirmation with details"
        )
        
        try:
            result = await asyncio.to_thread(self.execute, confirmation_task)
        except AttributeError:
            result = await asyncio.to_thread(self.llm.call, confirmation_task.description)
        
        return {
            "agent_id": "executor",
            "confirmation": result,
            "execution_successful": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def create_llm(self, model_config: Dict):
        """Create LLM instance based on config"""
        model_name = model_config.get("model", "gpt-4")
        return ModelFactory.create_llm(model_name)
