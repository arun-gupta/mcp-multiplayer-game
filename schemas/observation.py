"""
Observation schema for Scout Agent
Defines what the scout can observe and report back to the strategist
"""
from pydantic import BaseModel
from typing import List, Optional

class BoardPosition(BaseModel):
    """Represents a position on the Tic Tac Toe board"""
    row: int  # 0-2
    col: int  # 0-2
    value: str  # "X", "O", or ""

class GameHistory(BaseModel):
    """Represents a single move in the game"""
    move_number: int
    player: str  # "player" or "ai"
    position: BoardPosition
    result: Optional[str] = None  # "win", "lose", "draw", or None if game continues

class Observation(BaseModel):
    """Scout agent's observation of the current game state"""
    current_board: List[List[str]]  # 3x3 board with "X", "O", or ""
    current_player: str  # "player" or "ai"
    move_number: int
    game_history: List[GameHistory]
    available_moves: List[BoardPosition]  # Empty positions
    player_symbol: str = "X"  # Player's symbol
    ai_symbol: str = "O"  # AI's symbol
    game_over: bool = False
    winner: Optional[str] = None  # "player", "ai", "draw", or None
    last_move: Optional[BoardPosition] = None
    threats: List[BoardPosition] = []  # Positions that could lead to immediate win
    blocking_moves: List[BoardPosition] = []  # Positions that block opponent's win 