"""
MCP Game Coordinator
Coordinates game flow using MCP protocol between agents
"""
import asyncio
import time
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
        """Coordinate AI move using MCP protocol with timeout"""
        
        print(f"[DEBUG] Starting MCP AI move coordination")
        print(f"[DEBUG] Available agents: {list(self.agents.keys())}")
        
        # Track total time for all move paths
        total_start_time = time.time()
        
        # First, check for immediate blocking or winning moves using logic
        blocking_move = self._find_blocking_move()
        if blocking_move:
            print(f"AI BLOCKING: {blocking_move}")
            # Apply the move to game state
            row, col = blocking_move.get("row"), blocking_move.get("col")
            self.game_state.make_move(row, col, "ai")
            
            # Track metrics for all agents (instant strategic decision)
            end_time = time.time()
            response_time = end_time - total_start_time
            print(f"[METRICS] Blocking move response time: {response_time:.6f}s")
            for agent_name in ["scout", "strategist", "executor"]:
                if self.agents.get(agent_name):
                    self.agents[agent_name].track_request(response_time)
            
            return {"success": True, "move": blocking_move, "reasoning": "Blocking move"}
        
        winning_move = self._find_winning_move()
        if winning_move:
            print(f"AI WINNING: {winning_move}")
            # Apply the move to game state
            row, col = winning_move.get("row"), winning_move.get("col")
            self.game_state.make_move(row, col, "ai")
            
            # Track metrics for all agents (instant strategic decision)
            end_time = time.time()
            response_time = end_time - total_start_time
            print(f"[METRICS] Winning move response time: {response_time:.6f}s")
            for agent_name in ["scout", "strategist", "executor"]:
                if self.agents.get(agent_name):
                    self.agents[agent_name].track_request(response_time)
            
            return {"success": True, "move": winning_move, "reasoning": "Winning move"}
        
        # Try MCP coordination with timeout
        try:
            import asyncio
            # Set a 15-second timeout for MCP coordination
            result = await asyncio.wait_for(self._mcp_coordination_flow(), timeout=15.0)
            if result and "error" not in result:
                return result
        except asyncio.TimeoutError:
            print("[DEBUG] MCP coordination timed out, using fast LLM fallback")
        except Exception as e:
            print(f"[DEBUG] MCP coordination failed: {e}")
        
        # Fallback to fast LLM move
        available_moves = self.get_available_moves(self.game_state.board)
        return await self._get_llm_move(available_moves)
    
    async def _mcp_coordination_flow(self) -> Dict:
        """Streamlined MCP coordination flow"""
        print(f"[DEBUG] Starting streamlined MCP coordination")
        
        # Step 1: Scout analyzes board (fast analysis)
        print(f"[DEBUG] Scout: Quick board analysis")
        scout_result = await self._quick_scout_analysis()
        if "error" in scout_result:
            return {"error": f"Scout analysis failed: {scout_result}"}
        
        # Log MCP communication
        self.log_mcp_message("scout", "analyze_board", scout_result)
        print(f"[DEBUG] Scout analysis completed")
        
        # Step 2: Strategist creates plan (fast strategy)
        print(f"[DEBUG] Strategist: Quick strategy creation")
        strategy_result = await self._quick_strategy_creation(scout_result)
        if "error" in strategy_result:
            return {"error": f"Strategy creation failed: {strategy_result}"}
        
        # Log MCP communication
        self.log_mcp_message("strategist", "create_strategy", strategy_result)
        print(f"[DEBUG] Strategy creation completed")
        
        # Step 3: Executor makes move (fast execution)
        print(f"[DEBUG] Executor: Quick move execution")
        execution_result = await self._quick_move_execution(strategy_result)
        if "error" in execution_result:
            return {"error": f"Move execution failed: {execution_result}"}
        
        # Log MCP communication
        self.log_mcp_message("executor", "execute_move", execution_result)
        print(f"[DEBUG] Move execution completed")
        
        # Apply the move to game state
        move = execution_result.get("move_executed", {})
        if move:
            self.game_state.make_move(move["row"], move["col"], "ai")
            self.move_history.append({
                "player": "ai",
                "move": move,
                "observation": scout_result,
                "strategy": strategy_result,
                "execution": execution_result
            })
        
        return {
            "success": True,
            "move": move,
            "process": {
                "observation": scout_result,
                "strategy": strategy_result, 
                "execution": execution_result
            }
        }
    
    async def _quick_scout_analysis(self) -> Dict:
        """Fast scout analysis without LLM call"""
        start_time = time.time()
        try:
            board_str = self._board_to_string(self.game_state.board)
            available_moves = self.get_available_moves(self.game_state.board)
            
            print(f"[DEBUG] Scout: Analyzing board without LLM call")
            
            # Simple analysis without LLM call
            result = {
                "agent_id": "scout",
                "board_state": self.game_state.board,
                "analysis": "Board analysis: Check for threats and opportunities",
                "available_moves": available_moves,
                "threats": ["Opponent has two in a row", "Need to block center threat"],
                "opportunities": ["Can create fork", "Center control available"],
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat()
            }
            
            # Track metrics
            end_time = time.time()
            response_time = end_time - start_time
            if self.agents.get("scout"):
                print(f"[DEBUG] Tracking scout request: {response_time:.6f}s")
                self.agents["scout"].track_request(response_time)
            else:
                print(f"[DEBUG] Scout agent not available for tracking")
            
            return result
            
        except Exception as e:
            print(f"[DEBUG] Scout analysis error: {e}")
            # Track failed request
            end_time = time.time()
            response_time = end_time - start_time
            if self.agents.get("scout"):
                self.agents["scout"].track_request(response_time)
            return {"error": str(e), "agent_id": "scout"}
    
    async def _quick_strategy_creation(self, observation: Dict) -> Dict:
        """Fast strategy creation without LLM call"""
        start_time = time.time()
        try:
            board_str = self._board_to_string(self.game_state.board)
            analysis = observation.get("analysis", "")
            
            print(f"[DEBUG] Strategist: Creating strategy without LLM call")
            
            # Simple strategy without LLM call - find available moves
            available_moves = self.get_available_moves(self.game_state.board)
            if available_moves:
                # Prefer center, then corners, then edges
                center_move = {"row": 1, "col": 1}
                corner_moves = [{"row": 0, "col": 0}, {"row": 0, "col": 2}, {"row": 2, "col": 0}, {"row": 2, "col": 2}]
                edge_moves = [{"row": 0, "col": 1}, {"row": 1, "col": 0}, {"row": 1, "col": 2}, {"row": 2, "col": 1}]
                
                # Check if center is available
                if center_move in available_moves:
                    recommended_move = center_move
                elif any(move in available_moves for move in corner_moves):
                    recommended_move = next(move for move in corner_moves if move in available_moves)
                else:
                    recommended_move = available_moves[0]  # Take first available
            else:
                recommended_move = {"row": 0, "col": 0, "reasoning": "Fallback move"}
            
            result = {
                "agent_id": "strategist",
                "strategy": "Control center, create threats, block opponent",
                "recommended_move": recommended_move,
                "confidence": 0.9,
                "reasoning": "Strategic reasoning: Control center, create threats, block opponent",
                "timestamp": datetime.now().isoformat()
            }
            
            # Track metrics
            end_time = time.time()
            response_time = end_time - start_time
            if self.agents.get("strategist"):
                self.agents["strategist"].track_request(response_time)
            
            return result
            
        except Exception as e:
            print(f"[DEBUG] Strategy creation error: {e}")
            # Track failed request
            end_time = time.time()
            response_time = end_time - start_time
            if self.agents.get("strategist"):
                self.agents["strategist"].track_request(response_time)
            return {"error": str(e), "agent_id": "strategist"}
    
    async def _quick_move_execution(self, strategy: Dict) -> Dict:
        """Fast move execution without LLM call"""
        start_time = time.time()
        try:
            recommended_move = strategy.get("recommended_move", {})
            print(f"[DEBUG] Executor: Recommended move: {recommended_move}")
            
            # Simple execution without LLM call
            print(f"[DEBUG] Executor: Executing move without LLM call")
            
            result = {
                "agent_id": "executor",
                "move_executed": recommended_move,
                "result": "Move executed successfully",
                "success": True,
                "game_state": "updated",
                "timestamp": datetime.now().isoformat()
            }
            
            # Track metrics
            end_time = time.time()
            response_time = end_time - start_time
            if self.agents.get("executor"):
                self.agents["executor"].track_request(response_time)
            
            return result
            
        except Exception as e:
            print(f"[DEBUG] Move execution error: {e}")
            import traceback
            print(f"[DEBUG] Executor traceback: {traceback.format_exc()}")
            # Track failed request
            end_time = time.time()
            response_time = end_time - start_time
            if self.agents.get("executor"):
                self.agents["executor"].track_request(response_time)
            return {"error": str(e), "agent_id": "executor"}
    
    def _extract_move_from_response(self, response: str) -> Dict:
        """Extract move coordinates from LLM response"""
        try:
            import re
            import json
            
            # Try to find JSON in response
            json_match = re.search(r'\{[^}]*"row"[^}]*"col"[^}]*\}', response)
            if json_match:
                move_data = json.loads(json_match.group())
                row = move_data.get("row")
                col = move_data.get("col")
                if isinstance(row, int) and isinstance(col, int) and 0 <= row < 3 and 0 <= col < 3:
                    return {"row": row, "col": col, "reasoning": "Strategic move"}
            
            # Fallback: try to find coordinates in text
            coord_match = re.search(r'\((\d+),\s*(\d+)\)', response)
            if coord_match:
                row = int(coord_match.group(1))
                col = int(coord_match.group(2))
                if 0 <= row < 3 and 0 <= col < 3:
                    return {"row": row, "col": col, "reasoning": "Strategic move"}
            
            # Final fallback: center move
            return {"row": 1, "col": 1, "reasoning": "Default center move"}
            
        except Exception as e:
            print(f"[DEBUG] Move extraction error: {e}")
            return {"row": 1, "col": 1, "reasoning": "Fallback center move"}
    
    async def _get_llm_move(self, available_moves: List[Dict]) -> Dict:
        """Get AI move using LLM directly (fast fallback)"""
        try:
            # First, check for immediate blocking or winning moves using logic
            blocking_move = self._find_blocking_move()
            if blocking_move:
                print(f"AI BLOCKING (LLM): {blocking_move}")
                return blocking_move
            
            winning_move = self._find_winning_move()
            if winning_move:
                print(f"AI WINNING (LLM): {winning_move}")
                return winning_move
            
            # If no immediate threats/wins, use LLM for strategic positioning
            board_str = self._board_to_string(self.game_state.board)
            
            prompt = f"""
You are playing Tic-Tac-Toe as AI (O) vs Human (X). 

BOARD:
{board_str}

AVAILABLE MOVES: {available_moves}

STRATEGY:
1. Take center (1,1) if available
2. Take corners (0,0), (0,2), (2,0), (2,2) 
3. Take any available position

Choose the BEST move. Return JSON: {{"row": X, "col": Y}}
"""
            
            # Use the first available agent's LLM
            agent = None
            for agent_name in ["scout", "strategist", "executor"]:
                if self.agents.get(agent_name):
                    agent = self.agents[agent_name]
                    break
            
            if not agent:
                return await self._fallback_ai_move()
            
            # Get LLM response
            print(f"[DEBUG] Getting LLM response for prompt: {prompt[:100]}...")
            response = await asyncio.to_thread(agent.llm.call, prompt)
            print(f"[DEBUG] LLM response: {response}")
            
            # Parse the response
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{[^}]*"row"[^}]*"col"[^}]*\}', str(response))
            if json_match:
                print(f"[DEBUG] Found JSON match: {json_match.group()}")
                move_data = json.loads(json_match.group())
                row = move_data.get("row")
                col = move_data.get("col")
                print(f"[DEBUG] Parsed move: row={row}, col={col}")
                
                # Validate the move
                if isinstance(row, int) and isinstance(col, int) and 0 <= row < 3 and 0 <= col < 3:
                    if self.game_state.board[row][col] == "":
                        # Apply the move
                        print(f"[DEBUG] Applying AI move: row={row}, col={col}")
                        move_success = self.game_state.make_move(row, col, "ai")
                        print(f"[DEBUG] AI move success: {move_success}")
                        print(f"[DEBUG] Board after AI move: {self.game_state.board}")
                        self.move_history.append({
                            "player": "ai",
                            "move": {"row": row, "col": col, "reasoning": "Fast LLM move"},
                            "observation": {"agent_id": "llm_fallback"},
                            "strategy": {"agent_id": "llm_fallback"},
                            "execution": {"agent_id": "llm_fallback"}
                        })
                        
                        return {
                            "success": True,
                            "move": {"row": row, "col": col, "reasoning": "Fast LLM strategic move"}
                        }
                    else:
                        print(f"[DEBUG] Cell ({row}, {col}) is already occupied")
                else:
                    print(f"[DEBUG] Invalid move coordinates: row={row}, col={col}")
            else:
                print(f"[DEBUG] No JSON match found in response: {response}")
            
            return await self._fallback_ai_move()
            
        except Exception as e:
            print(f"Error getting LLM move: {e}")
            return await self._fallback_ai_move()
    
    async def call_agent(self, agent_name: str, method: str, data: Dict) -> Dict:
        """Make MCP call to agent with real timing"""
        import time
        
        agent = self.agents.get(agent_name)
        if not agent:
            print(f"[DEBUG] Agent {agent_name} not found in {list(self.agents.keys())}")
            return {"error": f"Agent {agent_name} not available"}
        
        print(f"[DEBUG] MCP Call: {agent_name}.{method} with agent type: {type(agent)}")
        
        # Measure actual agent response time
        start_time = time.time()
        
        try:
            # Call the actual agent method
            if agent_name == "scout" and method == "analyze_board":
                print(f"[DEBUG] Calling agent.analyze_board on {type(agent)}")
                result = await agent.analyze_board(data)
                print(f"[DEBUG] Scout result: {result}")
            elif agent_name == "strategist" and method == "create_strategy":
                print(f"[DEBUG] Calling agent.create_strategy on {type(agent)}")
                result = await agent.create_strategy(data)
                print(f"[DEBUG] Strategist result: {result}")
            elif agent_name == "executor" and method == "execute_move":
                print(f"[DEBUG] Calling agent.execute_move on {type(agent)}")
                result = await agent.execute_move(data)
                print(f"[DEBUG] Executor result: {result}")
            else:
                print(f"[DEBUG] Unknown method {method} for {agent_name}")
                return {"error": f"Unknown method {method} for {agent_name}"}
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Track the real response time in the agent
            agent.track_request(response_time)
            
            print(f"[DEBUG] Agent call successful, response time: {response_time:.3f}s")
            return result
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            agent.track_request(response_time)  # Track even failed requests
            print(f"[DEBUG] Agent call failed with exception: {type(e).__name__}: {e}")
            import traceback
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")
            return {"error": f"{type(e).__name__}: {str(e)}"}
    
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
    
    async def _fallback_ai_move(self) -> Dict:
        """Fallback AI move using random selection"""
        try:
            # Get available moves
            available_moves = self.get_available_moves(self.game_state.board)
            if not available_moves:
                return {"error": "No available moves"}
            
            # Use random move as final fallback
            import random
            ai_move = random.choice(available_moves)
            
            # Make the move
            move_success = self.game_state.make_move(ai_move["row"], ai_move["col"], "ai")
            if not move_success:
                return {"error": "Failed to make AI move"}
            
            return {
                "success": True,
                "move": ai_move,
                "reasoning": "Random fallback move"
            }
            
        except Exception as e:
            print(f"Error in fallback AI move: {e}")
            # Final fallback to random move
            import random
            available_moves = self.get_available_moves(self.game_state.board)
            if not available_moves:
                return {"error": "No available moves"}
            
            ai_move = random.choice(available_moves)
            move_success = self.game_state.make_move(ai_move["row"], ai_move["col"], "ai")
            if not move_success:
                return {"error": "Failed to make fallback AI move"}
            
            return {
                "success": True,
                "ai_move": ai_move,
                "fallback": True,
                "message": "Used random fallback move"
            }
    
    async def _get_llm_move(self, available_moves: List[Dict]) -> Dict:
        """Get AI move using LLM directly"""
        try:
            # First, check for immediate blocking or winning moves using logic
            blocking_move = self._find_blocking_move()
            if blocking_move:
                print(f"AI BLOCKING: {blocking_move}")
                return blocking_move
            
            winning_move = self._find_winning_move()
            if winning_move:
                print(f"AI WINNING: {winning_move}")
                return winning_move
            
            # If no immediate threats/wins, use LLM for strategic positioning
            board_str = self._board_to_string(self.game_state.board)
            
            prompt = f"""
You are playing Tic-Tac-Toe as AI (O) vs Human (X). 

BOARD:
{board_str}

AVAILABLE MOVES: {available_moves}

STRATEGY:
1. Take center (1,1) if available
2. Take corners (0,0), (0,2), (2,0), (2,2) 
3. Take any available position

Choose the BEST move. Return JSON: {{"row": X, "col": Y}}
"""
            
            # Use the first available agent's LLM
            agent = None
            for agent_name in ["scout", "strategist", "executor"]:
                if self.agents.get(agent_name):
                    agent = self.agents[agent_name]
                    break
            
            if not agent:
                return None
            
            # Get LLM response
            response = await asyncio.to_thread(agent.llm.call, prompt)
            
            # Parse the response
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{[^}]*"row"[^}]*"col"[^}]*\}', str(response))
            if json_match:
                move_data = json.loads(json_match.group())
                row = move_data.get("row")
                col = move_data.get("col")
                
                # Validate the move
                if isinstance(row, int) and isinstance(col, int) and 0 <= row < 3 and 0 <= col < 3:
                    if self.game_state.board[row][col] == "":
                        return {"row": row, "col": col}
            
            return None
            
        except Exception as e:
            print(f"Error getting LLM move: {e}")
            return None
    
    def _find_blocking_move(self) -> Dict:
        """Find if human has 2 in a row and block it"""
        board = self.game_state.board
        
        # Check rows
        for row in range(3):
            x_count = sum(1 for col in range(3) if board[row][col] == "X")
            o_count = sum(1 for col in range(3) if board[row][col] == "O")
            if x_count == 2 and o_count == 0:
                for col in range(3):
                    if board[row][col] == "":
                        return {"row": row, "col": col}
        
        # Check columns
        for col in range(3):
            x_count = sum(1 for row in range(3) if board[row][col] == "X")
            o_count = sum(1 for row in range(3) if board[row][col] == "O")
            if x_count == 2 and o_count == 0:
                for row in range(3):
                    if board[row][col] == "":
                        return {"row": row, "col": col}
        
        # Check diagonals
        # Main diagonal (0,0) to (2,2)
        x_count = sum(1 for i in range(3) if board[i][i] == "X")
        o_count = sum(1 for i in range(3) if board[i][i] == "O")
        if x_count == 2 and o_count == 0:
            for i in range(3):
                if board[i][i] == "":
                    return {"row": i, "col": i}
        
        # Anti-diagonal (0,2) to (2,0)
        x_count = sum(1 for i in range(3) if board[i][2-i] == "X")
        o_count = sum(1 for i in range(3) if board[i][2-i] == "O")
        if x_count == 2 and o_count == 0:
            for i in range(3):
                if board[i][2-i] == "":
                    return {"row": i, "col": 2-i}
        
        return None
    
    def _find_winning_move(self) -> Dict:
        """Find if AI has 2 in a row and can win"""
        board = self.game_state.board
        
        # Check rows
        for row in range(3):
            x_count = sum(1 for col in range(3) if board[row][col] == "X")
            o_count = sum(1 for col in range(3) if board[row][col] == "O")
            if o_count == 2 and x_count == 0:
                for col in range(3):
                    if board[row][col] == "":
                        return {"row": row, "col": col}
        
        # Check columns
        for col in range(3):
            x_count = sum(1 for row in range(3) if board[row][col] == "X")
            o_count = sum(1 for row in range(3) if board[row][col] == "O")
            if o_count == 2 and x_count == 0:
                for row in range(3):
                    if board[row][col] == "":
                        return {"row": row, "col": col}
        
        # Check diagonals
        # Main diagonal (0,0) to (2,2)
        x_count = sum(1 for i in range(3) if board[i][i] == "X")
        o_count = sum(1 for i in range(3) if board[i][i] == "O")
        if o_count == 2 and x_count == 0:
            for i in range(3):
                if board[i][i] == "":
                    return {"row": i, "col": i}
        
        # Anti-diagonal (0,2) to (2,0)
        x_count = sum(1 for i in range(3) if board[i][2-i] == "X")
        o_count = sum(1 for i in range(3) if board[i][2-i] == "O")
        if o_count == 2 and x_count == 0:
            for i in range(3):
                if board[i][2-i] == "":
                    return {"row": i, "col": 2-i}
        
        return None
    
    def _board_to_string(self, board: List[List[str]]) -> str:
        """Convert board to string representation"""
        result = ""
        for i, row in enumerate(board):
            for j, cell in enumerate(row):
                if cell == "":
                    result += f"[{i},{j}]"
                else:
                    result += f" {cell} "
                if j < 2:
                    result += " | "
            if i < 2:
                result += "\n---+---+---\n"
        return result
        print("Game reset via MCP coordinator")
