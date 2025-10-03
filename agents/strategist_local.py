"""
Strategist MCP Agent Module
Strategist agent with MCP capabilities for distributed communication
"""
from .base_mcp_agent import BaseMCPAgent
from crewai import Task
from typing import Dict, List
import asyncio
import json
from datetime import datetime
from models.factory import ModelFactory
from utils.config import config


class StrategistMCPAgent(BaseMCPAgent):
    """Strategist agent with MCP capabilities"""
    
    def __init__(self, model_config: Dict):
        # Create LLM first
        llm = self.create_llm(model_config)
        
        super().__init__(
            role="Strategist Agent", 
            goal="Create optimal strategies based on board analysis",
            backstory="""You are a Tic Tac Toe master strategist with deep understanding of game theory
            and tactical positioning. Your expertise lies in prioritizing moves: first blocking
            opponent threats, then securing wins, then controlling center and corners for strategic
            advantage. You understand fork patterns, defensive positioning, and how to create
            multiple winning opportunities while preventing opponent victories.""",
            mcp_port=config.get_mcp_port("strategist"),  # ✅ Load from config
            agent_id="strategist",
            llm=llm
        )
    
    def register_agent_specific_endpoints(self):
        """Register Strategist-specific MCP tools with proper schemas"""
        self.register_mcp_tool(
            "create_strategy",
            self.create_strategy,
            "Generate optimal strategic plan based on board analysis",
            {
                "type": "object",
                "properties": {
                    "observation_data": {
                        "type": "object",
                        "description": "Board analysis from Scout agent"
                    }
                },
                "required": ["observation_data"]
            }
        )
        
        self.register_mcp_tool(
            "evaluate_position",
            self.evaluate_position,
            "Evaluate current position strength and strategic value",
            {
                "type": "object",
                "properties": {
                    "board_state": {
                        "type": "array",
                        "description": "3x3 game board"
                    },
                    "player": {
                        "type": "string",
                        "description": "Player to evaluate for (player or ai)"
                    }
                },
                "required": ["board_state", "player"]
            }
        )
        
        self.register_mcp_tool(
            "recommend_move",
            self.recommend_move,
            "Recommend best move with detailed strategic reasoning",
            {
                "type": "object",
                "properties": {
                    "board_state": {
                        "type": "array",
                        "description": "3x3 game board"
                    },
                    "available_moves": {
                        "type": "array",
                        "description": "List of available moves"
                    }
                },
                "required": ["board_state", "available_moves"]
            }
        )
        
        self.register_mcp_tool(
            "assess_win_probability",
            self.assess_win_probability,
            "Calculate win probability for current board position",
            {
                "type": "object",
                "properties": {
                    "board_state": {
                        "type": "array",
                        "description": "3x3 game board"
                    },
                    "player": {
                        "type": "string",
                        "description": "Player to assess (player or ai)"
                    }
                },
                "required": ["board_state", "player"]
            }
        )
    
    async def create_strategy(self, observation_data: Dict) -> Dict:
        """Create strategy based on Scout's observation"""
        try:
            # Extract data from Scout's observation
            board_state = observation_data.get("board_state", [])
            board_analysis = observation_data.get("analysis", "")
            threats = observation_data.get("threats", [])
            opportunities = observation_data.get("opportunities", [])
            analysis = board_analysis  # For fallback prompt
            
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
            
            # Execute using CrewAI with timeout
            try:
                strategy_result = await asyncio.wait_for(
                    self.execute(strategy_task),
                    timeout=15.0  # Increased timeout for LLM calls
                )
            except (AttributeError, asyncio.TimeoutError):
                # Fallback: use the LLM directly with optimized prompt
                short_prompt = f"""Create strategy for Tic Tac Toe.
Board: {json.dumps(board_state)}
Analysis: {analysis}
Recommend the best move with reasoning.
Keep response concise."""
                strategy_result = await asyncio.to_thread(self.llm.call, short_prompt)
            
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
        
        try:
            result = await self.execute(evaluation_task)
        except AttributeError:
            result = await self._tracked_llm_call(evaluation_task.description)
        
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
        
        try:
            result = await self.execute(recommendation_task)
        except AttributeError:
            result = await self._tracked_llm_call(recommendation_task.description)
        
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
        
        try:
            result = await self.execute(probability_task)
        except AttributeError:
            result = await self._tracked_llm_call(probability_task.description)
        
        return {
            "agent_id": "strategist",
            "win_probability": result,
            "confidence": 0.75,
            "timestamp": datetime.now().isoformat()
        }
    
    def extract_best_move(self, strategy_result: str) -> Dict:
        """Extract best move from strategy result"""
        import re

        # Try to find move in format (row, col) or [row, col] or row: X, col: Y
        patterns = [
            r'\((\d+),\s*(\d+)\)',  # (0, 1)
            r'\[(\d+),\s*(\d+)\]',  # [0, 1]
            r'row[:\s]+(\d+).*?col[:\s]+(\d+)',  # row: 0, col: 1
            r'position\s+\((\d+),\s*(\d+)\)',  # position (0, 1)
        ]

        for pattern in patterns:
            match = re.search(pattern, str(strategy_result), re.IGNORECASE)
            if match:
                row, col = int(match.group(1)), int(match.group(2))
                return {"row": row, "col": col, "reasoning": "Extracted from strategy"}

        # Fallback: return None to indicate no move found
        return None
    
    def extract_reasoning(self, strategy_result: str) -> str:
        """Extract reasoning from strategy result"""
        # TODO: Implement proper parsing of CrewAI result
        return "Strategic reasoning: Control center, create threats, block opponent"
    
    def create_llm(self, model_config: Dict):
        """Create LLM instance based on config"""
        model_name = model_config.get("model", "gpt-4")
        return ModelFactory.create_llm(model_name)
