"""
Strategist MCP Agent Module
Strategist agent with MCP capabilities for distributed communication
"""
from .base_mcp_agent import BaseMCPAgent
from crewai import Task
from typing import Dict, List
import asyncio
from datetime import datetime
from models.factory import ModelFactory


class StrategistMCPAgent(BaseMCPAgent):
    """Strategist agent with MCP capabilities"""
    
    def __init__(self, model_config: Dict):
        # Create LLM first
        llm = self.create_llm(model_config)
        
        super().__init__(
            role="Strategist Agent", 
            goal="Create optimal strategies based on board analysis",
            backstory="""You are a master strategist with deep understanding of Tic Tac Toe
            tactics. You excel at creating winning strategies and tactical plans.""",
            mcp_port=3002,
            agent_id="strategist",
            llm=llm
        )
    
    def register_agent_specific_endpoints(self):
        """Register Strategist-specific MCP endpoints"""
        self.register_handler("create_strategy", self.create_strategy)
        self.register_handler("evaluate_position", self.evaluate_position)
        self.register_handler("recommend_move", self.recommend_move)
        self.register_handler("assess_win_probability", self.assess_win_probability)
    
    async def create_strategy(self, observation_data: Dict) -> Dict:
        """Create strategy based on Scout's observation"""
        try:
            # Extract data from Scout's observation
            board_analysis = observation_data.get("analysis", "")
            threats = observation_data.get("threats", [])
            opportunities = observation_data.get("opportunities", [])
            
            # Create strategy task for CrewAI
            strategy_task = Task(
                description=f"""
                Based on this board analysis: {board_analysis}
                Threats identified: {threats}
                Opportunities: {opportunities}
                
                Create a strategic plan that:
                1. Prioritizes moves by importance
                2. Provides reasoning for each recommendation
                3. Includes fallback options
                4. Assesses win probability
                """,
                expected_output="Detailed strategic plan with prioritized moves"
            )
            
            # Execute using CrewAI
            strategy_result = await asyncio.to_thread(self.execute, strategy_task)
            
            return {
                "agent_id": "strategist",
                "strategy": strategy_result,
                "recommended_move": self.extract_best_move(strategy_result),
                "confidence": 0.90,
                "reasoning": self.extract_reasoning(strategy_result),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "agent_id": "strategist"}
    
    async def evaluate_position(self, board_data: Dict) -> Dict:
        """Evaluate the current position strength"""
        evaluation_task = Task(
            description=f"Evaluate the strategic strength of this position: {board_data.get('board')}",
            expected_output="Position evaluation with strategic assessment"
        )
        
        result = await asyncio.to_thread(self.execute, evaluation_task)
        
        return {
            "agent_id": "strategist",
            "position_evaluation": result,
            "strategic_advantage": "neutral",  # Extract from result
            "timestamp": datetime.now().isoformat()
        }
    
    async def recommend_move(self, context_data: Dict) -> Dict:
        """Recommend the best move based on context"""
        recommendation_task = Task(
            description=f"Recommend the best move based on: {context_data}",
            expected_output="Move recommendation with detailed reasoning"
        )
        
        result = await asyncio.to_thread(self.execute, recommendation_task)
        
        return {
            "agent_id": "strategist",
            "recommendation": result,
            "move": self.extract_best_move(result),
            "confidence": 0.88,
            "timestamp": datetime.now().isoformat()
        }
    
    async def assess_win_probability(self, game_state: Dict) -> Dict:
        """Assess the probability of winning from current position"""
        probability_task = Task(
            description=f"Assess win probability from this game state: {game_state}",
            expected_output="Win probability assessment with reasoning"
        )
        
        result = await asyncio.to_thread(self.execute, probability_task)
        
        return {
            "agent_id": "strategist",
            "win_probability": result,
            "confidence": 0.75,
            "timestamp": datetime.now().isoformat()
        }
    
    def extract_best_move(self, strategy_result: str) -> Dict:
        """Extract best move from strategy result"""
        # TODO: Implement proper parsing of CrewAI result
        # For now, return a mock move
        return {"row": 1, "col": 1, "reasoning": "Strategic center control"}
    
    def extract_reasoning(self, strategy_result: str) -> str:
        """Extract reasoning from strategy result"""
        # TODO: Implement proper parsing of CrewAI result
        return "Strategic reasoning: Control center, create threats, block opponent"
    
    def create_llm(self, model_config: Dict):
        """Create LLM instance based on config"""
        model_name = model_config.get("model", "gpt-4")
        return ModelFactory.create_llm(model_name)
