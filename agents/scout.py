"""
Scout MCP Agent Module
Scout agent with MCP capabilities for distributed communication
"""
from .base_mcp_agent import BaseMCPAgent
from crewai import Task
from typing import Dict, List
import json
import asyncio
from datetime import datetime
from models.factory import ModelFactory


class ScoutMCPAgent(BaseMCPAgent):
    """Scout agent with MCP capabilities"""
    
    def __init__(self, model_config: Dict):
        # Create LLM first
        llm = self.create_llm(model_config)
        
        super().__init__(
            role="Scout Agent",
            goal="Analyze the Tic Tac Toe board and detect threats, opportunities, and patterns",
            backstory="""You are a keen observer with exceptional pattern recognition abilities.
            Your role is to thoroughly analyze the current game state and provide detailed
            observations that will help the team make strategic decisions.""",
            mcp_port=3001,
            agent_id="scout",
            llm=llm
        )
    
    def register_agent_specific_endpoints(self):
        """Register Scout-specific MCP endpoints"""
        self.register_handler("analyze_board", self.analyze_board)
        self.register_handler("detect_threats", self.detect_threats)
        self.register_handler("identify_opportunities", self.identify_opportunities)
        self.register_handler("get_pattern_analysis", self.get_pattern_analysis)
    
    async def analyze_board(self, board_data: Dict) -> Dict:
        """Analyze board state and return comprehensive observation"""
        try:
            board_state = board_data.get("board", [])
            current_player = board_data.get("current_player", "ai")
            move_number = board_data.get("move_number", 0)
            
            # Create analysis task for CrewAI
            analysis_task = Task(
                description=f"""
                Analyze this Tic Tac Toe board state:
                Board: {json.dumps(board_state)}
                Current Player: {current_player}
                Move Number: {move_number}
                
                Provide analysis including:
                1. Available moves
                2. Immediate threats
                3. Blocking opportunities
                4. Winning opportunities
                5. Pattern assessment
                """,
                expected_output="Structured analysis with threats, opportunities, and recommendations"
            )
            
            # Execute analysis using CrewAI
            analysis_result = await asyncio.to_thread(self.execute, analysis_task)
            
            # Structure the response for MCP protocol
            return {
                "agent_id": "scout",
                "board_state": board_state,
                "analysis": analysis_result,
                "available_moves": self.get_available_moves(board_state),
                "threats": self.extract_threats(analysis_result),
                "opportunities": self.extract_opportunities(analysis_result),
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e), "agent_id": "scout"}
    
    async def detect_threats(self, board_data: Dict) -> Dict:
        """Detect immediate threats on the board"""
        # Use CrewAI's capabilities for threat detection
        threat_task = Task(
            description=f"Identify immediate threats in board: {board_data.get('board')}",
            expected_output="List of immediate threats and blocking moves"
        )
        
        result = await asyncio.to_thread(self.execute, threat_task)
        
        return {
            "agent_id": "scout",
            "threats": result,
            "critical_moves": [],  # Extract from result
            "timestamp": datetime.now().isoformat()
        }
    
    async def identify_opportunities(self, board_data: Dict) -> Dict:
        """Identify winning opportunities"""
        opportunity_task = Task(
            description=f"Identify winning opportunities in board: {board_data.get('board')}",
            expected_output="List of winning opportunities and strategic moves"
        )
        
        result = await asyncio.to_thread(self.execute, opportunity_task)
        
        return {
            "agent_id": "scout",
            "opportunities": result,
            "winning_moves": [],  # Extract from result
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_pattern_analysis(self, board_data: Dict) -> Dict:
        """Analyze patterns in the game"""
        pattern_task = Task(
            description=f"Analyze patterns and game phase in board: {board_data.get('board')}",
            expected_output="Pattern analysis including game phase, strategic themes, and player tendencies"
        )
        
        result = await asyncio.to_thread(self.execute, pattern_task)
        
        return {
            "agent_id": "scout",
            "patterns": result,
            "game_phase": "midgame",  # Extract from result
            "timestamp": datetime.now().isoformat()
        }
    
    def get_available_moves(self, board_state: List[List[str]]) -> List[Dict]:
        """Get available moves from board state"""
        available = []
        for row in range(3):
            for col in range(3):
                if board_state[row][col] == "":
                    available.append({"row": row, "col": col})
        return available
    
    def extract_threats(self, analysis_result: str) -> List[str]:
        """Extract threats from analysis result"""
        # TODO: Implement proper parsing of CrewAI result
        # For now, return mock data
        return ["Opponent has two in a row", "Need to block center threat"]
    
    def extract_opportunities(self, analysis_result: str) -> List[str]:
        """Extract opportunities from analysis result"""
        # TODO: Implement proper parsing of CrewAI result
        # For now, return mock data
        return ["Can create fork", "Center control available"]
    
    def create_llm(self, model_config: Dict):
        """Create LLM instance based on config"""
        model_name = model_config.get("model", "gpt-4")
        return ModelFactory.create_llm(model_name)
