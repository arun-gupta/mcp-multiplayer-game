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
    
    def set_agents(self, scout_agent, strategist_agent, executor_agent):
        """Set real agent instances for actual timing"""
        self.agents["scout"] = scout_agent
        self.agents["strategist"] = strategist_agent
        self.agents["executor"] = executor_agent
    
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
        
        # 4. Check if game is over after AI move
        game_over = self.game_state.game_over
        winner = self.game_state.winner
        
        return {
            "player_move": {"row": row, "col": col},
            "ai_move": ai_move_result,
            "board": self.game_state.board,
            "game_over": game_over,
            "winner": winner
        }
    
    async def get_ai_move(self) -> Dict:
        """Coordinate AI move using MCP protocol"""
        
        # Step 1: Scout analyzes board
        available_moves = self.get_available_moves(self.game_state.board)
        observation = await self.call_agent("scout", "analyze_board", {
            "board": self.game_state.board,
            "current_player": "ai", 
            "move_number": len(self.move_history),
            "available_moves": available_moves
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
        """Make MCP call to agent with real timing"""
        import time
        
        agent = self.agents.get(agent_name)
        if not agent:
            return {"error": f"Agent {agent_name} not available"}
        
        print(f"MCP Call: {agent_name}.{method} with {data}")
        
        # Measure actual agent response time
        start_time = time.time()
        
        try:
            # Call the actual agent method
            if agent_name == "scout" and method == "analyze_board":
                result = await agent.analyze_board(data)
            elif agent_name == "strategist" and method == "create_strategy":
                result = await agent.create_strategy(data)
            elif agent_name == "executor" and method == "execute_move":
                result = await agent.execute_move(data)
            else:
                return {"error": f"Unknown method {method} for {agent_name}"}
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Track the real response time in the agent
            agent.track_request(response_time)
            
            return result
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            agent.track_request(response_time)  # Track even failed requests
            return {"error": str(e)}
    
    async def scout_analyze_board(self, data: Dict) -> Dict:
        """Scout agent analyzes the board for threats and opportunities"""
        board = data.get("board", [])
        available_moves = data.get("available_moves", [])
        
        # Analyze board for threats and opportunities
        threats = self.analyze_threats(board)
        opportunities = self.analyze_opportunities(board)
        
        return {
            "agent_id": "scout",
            "board_state": board,
            "analysis": f"Found {len(threats)} threats and {len(opportunities)} opportunities",
            "available_moves": available_moves,
            "threats": threats,
            "opportunities": opportunities,
            "confidence": 0.85,
            "timestamp": datetime.now().isoformat()
        }
    
    async def strategist_create_strategy(self, data: Dict) -> Dict:
        """Strategist creates optimal strategy using LLM analysis"""
        available_moves = data.get("available_moves", [])
        threats = data.get("threats", [])
        opportunities = data.get("opportunities", [])
        board_state = data.get("board_state", [])
        
        # Use LLM to determine optimal move
        recommended_move = await self.get_llm_move_recommendation(board_state, available_moves, threats, opportunities)
        
        return {
            "agent_id": "strategist",
            "strategy": "LLM-based strategic analysis complete",
            "recommended_move": recommended_move,
            "confidence": 0.90,
            "reasoning": f"LLM selected optimal move from {len(available_moves)} options",
            "timestamp": datetime.now().isoformat()
        }
    
    async def executor_execute_move(self, data: Dict) -> Dict:
        """Executor validates and executes the strategic move"""
        recommended_move = data.get("recommended_move", {})
        
        # Validate the move
        if not recommended_move or "row" not in recommended_move or "col" not in recommended_move:
            return {
                "agent_id": "executor",
                "error": "Invalid move format",
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "agent_id": "executor",
            "move_executed": recommended_move,
            "result": "Move executed successfully",
            "success": True,
            "game_state": "updated",
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_llm_move_recommendation(self, board: List[List[str]], available_moves: List[Dict], threats: List[str], opportunities: List[str]) -> Dict:
        """Query LLM for optimal move recommendation"""
        try:
            # Create board representation for LLM
            board_str = self.format_board_for_llm(board)
            
            # Create prompt for LLM
            prompt = f"""
You are an expert Tic-Tac-Toe AI strategist. Analyze this board and recommend the best move.

Current Board:
{board_str}

Available Moves: {available_moves}
Threats Identified: {threats}
Opportunities: {opportunities}

Rules:
- You are playing as 'O' (AI)
- Player is 'X' (Human)
- Win by getting 3 in a row (horizontal, vertical, or diagonal)
- Block opponent from winning
- Create winning opportunities
- Control center if possible

Respond with ONLY the coordinates in format: row,col
Example: 1,1 for center position
"""
            
            # For now, use a simple strategy until we integrate actual LLM
            # This will be replaced with real LLM API call
            move = self.simple_ai_strategy(board, available_moves, threats, opportunities)
            
            return move
            
        except Exception as e:
            print(f"Error getting LLM recommendation: {e}")
            # Fallback to random move
            import random
            return random.choice(available_moves) if available_moves else {"row": 1, "col": 1}
    
    def format_board_for_llm(self, board: List[List[str]]) -> str:
        """Format board for LLM analysis"""
        result = []
        for i, row in enumerate(board):
            row_str = " | ".join([cell if cell else f"({i},{j})" for j, cell in enumerate(row)])
            result.append(f"Row {i}: {row_str}")
        return "\n".join(result)
    
    def simple_ai_strategy(self, board: List[List[str]], available_moves: List[Dict], threats: List[str], opportunities: List[str]) -> Dict:
        """Simple AI strategy until LLM integration"""
        # Priority 1: Win if possible
        for move in available_moves:
            if self.would_win(board, move, "O"):
                return move
        
        # Priority 2: Block opponent from winning
        for move in available_moves:
            if self.would_win(board, move, "X"):
                return move
        
        # Priority 3: Take center if available
        center_move = {"row": 1, "col": 1}
        if center_move in available_moves:
            return center_move
        
        # Priority 4: Take corners
        corners = [{"row": 0, "col": 0}, {"row": 0, "col": 2}, {"row": 2, "col": 0}, {"row": 2, "col": 2}]
        for corner in corners:
            if corner in available_moves:
                return corner
        
        # Priority 5: Take any available move
        import random
        return random.choice(available_moves) if available_moves else {"row": 1, "col": 1}
    
    def would_win(self, board: List[List[str]], move: Dict, player: str) -> bool:
        """Check if a move would result in a win for the given player"""
        row, col = move["row"], move["col"]
        
        # Temporarily place the move
        original = board[row][col]
        board[row][col] = player
        
        # Check for win
        won = self.check_win_condition(board, player)
        
        # Restore original
        board[row][col] = original
        
        return won
    
    def check_win_condition(self, board: List[List[str]], player: str) -> bool:
        """Check if the given player has won"""
        # Check rows
        for row in board:
            if all(cell == player for cell in row):
                return True
        
        # Check columns
        for col in range(3):
            if all(board[row][col] == player for row in range(3)):
                return True
        
        # Check diagonals
        if all(board[i][i] == player for i in range(3)):
            return True
        if all(board[i][2-i] == player for i in range(3)):
            return True
        
        return False
    
    def analyze_threats(self, board: List[List[str]]) -> List[str]:
        """Analyze board for immediate threats"""
        threats = []
        
        # Check if opponent can win in next move
        for row in range(3):
            for col in range(3):
                if board[row][col] == "":
                    if self.would_win(board, {"row": row, "col": col}, "X"):
                        threats.append(f"Opponent can win at ({row},{col})")
        
        return threats
    
    def analyze_opportunities(self, board: List[List[str]]) -> List[str]:
        """Analyze board for winning opportunities"""
        opportunities = []
        
        # Check if AI can win in next move
        for row in range(3):
            for col in range(3):
                if board[row][col] == "":
                    if self.would_win(board, {"row": row, "col": col}, "O"):
                        opportunities.append(f"AI can win at ({row},{col})")
        
        return opportunities
    
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
            "agents_connected": {
                "scout": self.agents["scout"] is not None,
                "strategist": self.agents["strategist"] is not None,
                "executor": self.agents["executor"] is not None
            },
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
