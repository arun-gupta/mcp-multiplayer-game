"""
MCP Game Coordinator
Coordinates game flow using MCP protocol between agents
"""
import asyncio
from typing import Dict, List
from datetime import datetime
from .state import TicTacToeGameState


class MCPGameCoordinator:
    """Coordinates game flow using MCP protocol between agents"""
    
    def __init__(self):
        self.game_state = TicTacToeGameState()
        self.agents = {
            "scout": None,     # Will connect to scout://localhost:3001
            "strategist": None, # Will connect to strategist://localhost:3002  
            "executor": None   # Will connect to executor://localhost:3003
        }
        self.move_history = []
        self.mcp_logs = []
    
    async def initialize_agents(self):
        """Initialize connections to MCP agent servers"""
        # TODO: Create actual MCP client connections
        print("Connecting to MCP agents...")
        
        # Mock connections for now
        self.agents["scout"] = "MockMCPClient(scout://localhost:3001)"
        self.agents["strategist"] = "MockMCPClient(strategist://localhost:3002)"
        self.agents["executor"] = "MockMCPClient(executor://localhost:3003)"
        
        print("MCP agent connections initialized")
    
    async def process_player_move(self, row: int, col: int) -> Dict:
        """Process player move and orchestrate AI response via MCP"""
        
        # 1. Update game state with player move
        move_success = self.game_state.make_move(row, col, "player")
        if not move_success:
            return {"success": False, "error": "Invalid move or game over"}
        
        # 2. Check if game is over
        if self.game_state._check_winner() or self.game_state.move_number >= 9:
            return {"game_over": True, "state": self.game_state.board}
        
        # 3. Get AI response via MCP protocol
        ai_move_result = await self.get_ai_move()
        
        return {
            "player_move": {"row": row, "col": col},
            "ai_move": ai_move_result,
            "board": self.game_state.board,
            "game_over": self.game_state._check_winner() is not None
        }
    
    async def get_ai_move(self) -> Dict:
        """Coordinate AI move using MCP protocol"""
        
        # Step 1: Scout analyzes board
        observation = await self.call_agent("scout", "analyze_board", {
            "board": self.game_state.board,
            "current_player": "ai", 
            "move_number": len(self.move_history)
        })
        
        if "error" in observation:
            return {"error": "Scout analysis failed", "details": observation}
        
        # Log MCP communication
        self.log_mcp_message("scout", "analyze_board", observation)
        
        # Step 2: Strategist creates plan
        strategy = await self.call_agent("strategist", "create_strategy", observation)
        
        if "error" in strategy:
            return {"error": "Strategy creation failed", "details": strategy}
        
        # Log MCP communication
        self.log_mcp_message("strategist", "create_strategy", strategy)
        
        # Step 3: Executor makes move
        execution = await self.call_agent("executor", "execute_move", strategy)
        
        if "error" in execution:
            return {"error": "Move execution failed", "details": execution}
        
        # Log MCP communication
        self.log_mcp_message("executor", "execute_move", execution)
        
        # Apply the move to game state
        move = execution.get("move_executed", {})
        if move:
            self.game_state.make_move(move["row"], move["col"], "ai")
            self.move_history.append({
                "player": "ai",
                "move": move,
                "observation": observation,
                "strategy": strategy,
                "execution": execution
            })
        
        return {
            "success": True,
            "move": move,
            "process": {
                "observation": observation,
                "strategy": strategy, 
                "execution": execution
            }
        }
    
    async def call_agent(self, agent_name: str, method: str, data: Dict) -> Dict:
        """Make MCP call to agent"""
        # TODO: Implement actual MCP client calls
        print(f"MCP Call: {agent_name}.{method} with {data}")
        
        # Mock response for now - simulate agent processing
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Return mock response based on agent and method
        if agent_name == "scout":
            if method == "analyze_board":
                return {
                    "agent_id": "scout",
                    "board_state": data.get("board", []),
                    "analysis": "Board analysis complete",
                    "available_moves": self.get_available_moves(data.get("board", [])),
                    "threats": ["Opponent has two in a row"],
                    "opportunities": ["Can create fork"],
                    "confidence": 0.85,
                    "timestamp": datetime.now().isoformat()
                }
        
        elif agent_name == "strategist":
            if method == "create_strategy":
                return {
                    "agent_id": "strategist",
                    "strategy": "Strategic plan created",
                    "recommended_move": {"row": 1, "col": 1},
                    "confidence": 0.90,
                    "reasoning": "Control center for strategic advantage",
                    "timestamp": datetime.now().isoformat()
                }
        
        elif agent_name == "executor":
            if method == "execute_move":
                return {
                    "agent_id": "executor",
                    "move_executed": data.get("recommended_move", {"row": 1, "col": 1}),
                    "result": "Move executed successfully",
                    "success": True,
                    "game_state": "updated",
                    "timestamp": datetime.now().isoformat()
                }
        
        # Default mock response
        return {
            "agent_id": agent_name,
            "method": method,
            "mock_response": True,
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
    
    def log_mcp_message(self, agent: str, message_type: str, data: Dict):
        """Log MCP protocol message"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "message_type": message_type,
            "data": data
        }
        self.mcp_logs.append(log_entry)
        print(f"[MCP] {agent} -> {message_type}: {data}")
    
    def get_agent_status(self) -> Dict:
        """Get status of all agents"""
        return {
            "coordinator_status": "running",
            "agents": self.agents,
            "game_state": self.game_state.board,
            "move_count": len(self.move_history),
            "mcp_logs_count": len(self.mcp_logs)
        }
    
    def get_mcp_logs(self) -> List[Dict]:
        """Get MCP protocol logs"""
        return self.mcp_logs
    
    def reset_game(self):
        """Reset the game state"""
        self.game_state = TicTacToeGameState()
        self.move_history = []
        self.mcp_logs = []
        print("Game reset via MCP coordinator")
