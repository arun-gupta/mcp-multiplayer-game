"""
Game State Module
Manages the overall game state, turn management, and game progression
"""
import random
from datetime import datetime
from typing import List, Optional, Tuple
from schemas.observation import Observation, GameHistory, BoardPosition

class TicTacToeGameState:
    """Manages the state of a Tic Tac Toe game"""
    
    def __init__(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "player"  # "player" or "ai"
        self.move_number = 0
        self.game_history: List[GameHistory] = []
        self.game_over = False
        self.winner = None
        self.player_symbol = "X"
        self.ai_symbol = "O"
        
        # Metrics tracking
        self.game_start_time = datetime.now()
        self.mcp_message_count = 0
        self.agent_response_times = {
            "scout": [],
            "strategist": [],
            "executor": []
        }
        self.llm_costs = {
            "gpt4": 0.0,
            "claude": 0.0,
            "llama": 0.0
        }
    
    def initialize_new_game(self):
        """Reset the game state for a new game"""
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "player"
        self.move_number = 0
        self.game_history = []
        self.game_over = False
        self.winner = None
        
        # Reset metrics
        self.game_start_time = datetime.now()
        self.mcp_message_count = 0
        self.agent_response_times = {
            "scout": [],
            "strategist": [],
            "executor": []
        }
        self.llm_costs = {
            "gpt4": 0.0,
            "claude": 0.0,
            "llama": 0.0
        }
    
    def increment_mcp_messages(self):
        """Increment MCP message counter"""
        self.mcp_message_count += 1
    
    def add_response_time(self, agent: str, response_time_ms: float):
        """Add response time for an agent"""
        if agent in self.agent_response_times:
            self.agent_response_times[agent].append(response_time_ms)
    
    def add_llm_cost(self, llm: str, cost: float):
        """Add cost for an LLM"""
        if llm in self.llm_costs:
            self.llm_costs[llm] += cost
    
    def get_metrics(self) -> dict:
        """Get current metrics"""
        game_duration = (datetime.now() - self.game_start_time).total_seconds()
        
        # Calculate average response times
        avg_response_times = {}
        for agent, times in self.agent_response_times.items():
            avg_response_times[agent] = sum(times) / len(times) if times else 0
        
        # Calculate total cost
        total_cost = sum(self.llm_costs.values())
        
        return {
            "mcp_message_count": self.mcp_message_count,
            "game_duration_seconds": game_duration,
            "avg_response_times": avg_response_times,
            "llm_costs": self.llm_costs,
            "total_cost": total_cost
        }
    
    def get_available_moves(self) -> List[BoardPosition]:
        """Get all available (empty) positions on the board"""
        moves = []
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == "":
                    moves.append(BoardPosition(row=row, col=col, value=""))
        return moves
    
    def make_move(self, row: int, col: int, player: str) -> bool:
        """Make a move on the board"""
        if self.game_over or self.board[row][col] != "":
            return False
        
        symbol = self.player_symbol if player == "player" else self.ai_symbol
        self.board[row][col] = symbol
        self.move_number += 1
        
        # Record the move
        position = BoardPosition(row=row, col=col, value=symbol)
        move_history = GameHistory(
            move_number=self.move_number,
            player=player,
            position=position
        )
        self.game_history.append(move_history)
        
        # Check for game over
        self._check_game_over()
        
        # Switch players
        if not self.game_over:
            self.current_player = "ai" if player == "player" else "player"
        
        return True
    
    def _check_game_over(self):
        """Check if the game is over (win, lose, or draw)"""
        # Check for win
        winner = self._check_winner()
        if winner:
            self.game_over = True
            self.winner = winner
            # Update the last move with result
            if self.game_history:
                self.game_history[-1].result = "win" if winner == self.current_player else "lose"
            return
        
        # Check for draw
        if self.move_number >= 9:
            self.game_over = True
            self.winner = "draw"
            if self.game_history:
                self.game_history[-1].result = "draw"
    
    def _check_winner(self) -> Optional[str]:
        """Check if there's a winner"""
        # Check rows
        for row in range(3):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] != "":
                return "player" if self.board[row][0] == self.player_symbol else "ai"
        
        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != "":
                return "player" if self.board[0][col] == self.player_symbol else "ai"
        
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != "":
            return "player" if self.board[0][0] == self.player_symbol else "ai"
        
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != "":
            return "player" if self.board[0][2] == self.player_symbol else "ai"
        
        return None
    
    def get_threats(self) -> List[BoardPosition]:
        """Get positions that could lead to immediate win for AI"""
        threats = []
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == "":
                    # Test if this move would win
                    self.board[row][col] = self.ai_symbol
                    if self._check_winner() == "ai":
                        threats.append(BoardPosition(row=row, col=col, value=""))
                    self.board[row][col] = ""
        return threats
    
    def get_blocking_moves(self) -> List[BoardPosition]:
        """Get positions that block player's immediate win"""
        blocking = []
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == "":
                    # Test if this move would win for player
                    self.board[row][col] = self.player_symbol
                    if self._check_winner() == "player":
                        blocking.append(BoardPosition(row=row, col=col, value=""))
                    self.board[row][col] = ""
        return blocking
    
    def get_observation(self) -> Observation:
        """Get the current game state as an observation for the Scout agent"""
        return Observation(
            current_board=self.board,
            current_player=self.current_player,
            move_number=self.move_number,
            game_history=self.game_history,
            available_moves=self.get_available_moves(),
            player_symbol=self.player_symbol,
            ai_symbol=self.ai_symbol,
            game_over=self.game_over,
            winner=self.winner,
            last_move=self.game_history[-1].position if self.game_history else None,
            threats=self.get_threats(),
            blocking_moves=self.get_blocking_moves()
        )
    
    def generate_ai_move(self) -> Tuple[int, int]:
        """Generate AI's move using simple strategy"""
        import random
        
        # First priority: Win if possible
        threats = self.get_threats()
        if threats:
            pos = random.choice(threats)
            return pos.row, pos.col
        
        # Second priority: Block player's win
        blocking = self.get_blocking_moves()
        if blocking:
            pos = random.choice(blocking)
            return pos.row, pos.col
        
        # Third priority: Take center
        if self.board[1][1] == "":
            return 1, 1
        
        # Fourth priority: Take corners
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        available_corners = [(r, c) for r, c in corners if self.board[r][c] == ""]
        if available_corners:
            return random.choice(available_corners)
        
        # Last resort: Take any available edge
        edges = [(0, 1), (1, 0), (1, 2), (2, 1)]
        available_edges = [(r, c) for r, c in edges if self.board[r][c] == ""]
        if available_edges:
            return random.choice(available_edges)
        
        # Should never reach here if game is not over
        return 0, 0
    
    def get_state_for_api(self) -> dict:
        """Get the current game state formatted for API response"""
        return {
            "board": self.board,
            "current_player": self.current_player,
            "move_number": self.move_number,
            "game_over": self.game_over,
            "winner": self.winner,
            "game_history": [move.dict() for move in self.game_history],
            "available_moves": [move.dict() for move in self.get_available_moves()],
            "statistics": {
                "total_moves": self.move_number,
                "player_moves": len([m for m in self.game_history if m.player == "player"]),
                "ai_moves": len([m for m in self.game_history if m.player == "ai"])
            }
        } 