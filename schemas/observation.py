"""
Observation schema for Scout Agent
Defines what the scout can observe and report back to the strategist
"""
from pydantic import BaseModel
from typing import List, Optional

class GameHistory(BaseModel):
    """Represents a single move in the game history"""
    round_number: int
    player_move: str  # "rock", "paper", "scissors"
    opponent_move: str  # "rock", "paper", "scissors"
    result: str  # "win", "lose", "draw"
    timestamp: str

class Observation(BaseModel):
    """Scout agent's observation of the current game state"""
    current_round: int
    player_score: int
    opponent_score: int
    game_history: List[GameHistory]
    last_opponent_moves: List[str]  # Last 3-5 moves for pattern analysis
    total_rounds_played: int
    current_streak: str  # "winning", "losing", "drawing"
    game_mode: str = "tournament"  # "tournament", "best_of_5", etc.
    max_rounds: int = 10 