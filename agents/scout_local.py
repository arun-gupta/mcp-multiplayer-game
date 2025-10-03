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
from utils.config import config


class ScoutMCPAgent(BaseMCPAgent):
    """Scout agent with MCP capabilities"""
    
    def __init__(self, model_config: Dict):
        # Create LLM first
        llm = self.create_llm(model_config)
        
        super().__init__(
            role="Scout Agent",
            goal="Analyze the Tic Tac Toe board and detect threats, opportunities, and patterns",
            backstory="""You are a Tic Tac Toe expert with exceptional pattern recognition abilities.
            Your specialty is identifying immediate threats where the opponent (X) has 2 in a row
            and must be blocked, as well as spotting winning opportunities where you (O) can
            complete a line. You excel at scanning all rows, columns, and diagonals for potential
            wins and blocks. Your analysis is critical for preventing losses and securing victories.""",
            mcp_port=config.get_mcp_port("scout"),  # ✅ Load from config
            agent_id="scout",
            llm=llm
        )
    
    def register_agent_specific_endpoints(self):
        """Register Scout-specific MCP tools with proper schemas"""
        self.register_mcp_tool(
            "analyze_board",
            self.analyze_board,
            "Analyze Tic-Tac-Toe board state and provide comprehensive insights",
            {
                "type": "object",
                "properties": {
                    "board": {
                        "type": "array",
                        "description": "3x3 game board"
                    },
                    "current_player": {
                        "type": "string",
                        "description": "Current player (player or ai)"
                    },
                    "move_number": {
                        "type": "integer",
                        "description": "Current move number"
                    }
                },
                "required": ["board"]
            }
        )
        
        self.register_mcp_tool(
            "detect_threats",
            self.detect_threats,
            "Identify immediate threats from opponent on the board",
            {
                "type": "object",
                "properties": {
                    "board": {
                        "type": "array",
                        "description": "3x3 game board"
                    }
                },
                "required": ["board"]
            }
        )
        
        self.register_mcp_tool(
            "identify_opportunities",
            self.identify_opportunities,
            "Find winning opportunities and strategic positions",
            {
                "type": "object",
                "properties": {
                    "board": {
                        "type": "array",
                        "description": "3x3 game board"
                    }
                },
                "required": ["board"]
            }
        )
        
        self.register_mcp_tool(
            "get_pattern_analysis",
            self.get_pattern_analysis,
            "Analyze game patterns, trends, and strategic themes",
            {
                "type": "object",
                "properties": {
                    "board": {
                        "type": "array",
                        "description": "3x3 game board"
                    },
                    "move_history": {
                        "type": "array",
                        "description": "History of moves played"
                    }
                },
                "required": ["board"]
            }
        )
    
    async def analyze_board(self, board_data: Dict) -> Dict:
        """Analyze board state and return comprehensive observation"""
        try:
            board_state = board_data.get("board", [])
            current_player = board_data.get("current_player", "ai")
            move_number = board_data.get("move_number", 0)
            
            # Create analysis task for CrewAI
            analysis_task = Task(
                description=f"""
                CRITICAL Tic Tac Toe board analysis:
                Board: {json.dumps(board_state)}
                Current Player: {current_player}
                Move Number: {move_number}
                
                URGENT PRIORITIES:
                1. THREAT DETECTION: Check if opponent (X) has 2 in a row - BLOCK immediately!
                2. WIN OPPORTUNITIES: Check if AI (O) has 2 in a row - WIN immediately!
                3. STRATEGIC ANALYSIS: Center control, corner positions, fork opportunities
                
                REQUIRED ANALYSIS:
                - Scan all rows, columns, and diagonals for threats
                - Identify any immediate blocking moves needed
                - Identify any winning moves available
                - Assess strategic positioning opportunities
                - Provide clear recommendations with reasoning
                """,
                expected_output="Structured analysis with immediate threats, blocking moves, winning opportunities, and strategic recommendations"
            )
            
            # Execute analysis using CrewAI with timeout
            try:
                print(f"[DEBUG] Scout: Starting CrewAI execution")
                # Use the CrewAI agent's execute method with timeout
                analysis_result = await asyncio.wait_for(
                    self.execute(analysis_task), 
                    timeout=15.0  # Increased timeout for LLM calls
                )
                print(f"[DEBUG] Scout: CrewAI execution completed")
            except Exception as e:
                print(f"[DEBUG] Scout: CrewAI execution failed with exception: {type(e).__name__}: {str(e)}")
                print(f"[DEBUG] Scout: Exception details: {repr(e)}")
                # Fallback: use the LLM directly with optimized prompt
                short_prompt = f"""Analyze this Tic Tac Toe board: {json.dumps(board_state)}
Current player: {current_player}

CRITICAL ANALYSIS REQUIRED:
1. THREAT DETECTION: Look for opponent (X) having 2 in a row - this is URGENT to block!
2. WIN OPPORTUNITIES: Look for AI (O) having 2 in a row - this is a winning move!
3. STRATEGIC POSITIONING: Center and corners are valuable

BOARD ANALYSIS:
- Check all rows, columns, and diagonals for threats
- Identify any immediate blocking moves needed
- Identify any winning moves available

Provide concise analysis focusing on immediate threats and opportunities."""
                analysis_result = await self._tracked_llm_call(short_prompt)
                print(f"[DEBUG] Scout: LLM fallback completed")
            
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
