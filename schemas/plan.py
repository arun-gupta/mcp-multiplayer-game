"""
Plan schema for Strategist Agent
Defines the strategic plan based on scout's observations
"""
from pydantic import BaseModel
from typing import List, Optional
from .observation import BoardPosition

class Strategy(BaseModel):
    """A single strategic move option"""
    position: BoardPosition
    move_type: str  # "winning", "blocking", "center", "corner", "edge", "random"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    expected_outcome: str  # "win", "draw", "continue", "uncertain"

class Plan(BaseModel):
    """Strategist agent's plan for the next move"""
    plan_id: str
    move_number: int
    current_board: List[List[str]]
    primary_strategy: Strategy
    alternative_strategies: List[Strategy]
    board_analysis: str  # Analysis of current board state
    threat_assessment: str  # "none", "low", "medium", "high", "critical"
    expected_player_move: Optional[BoardPosition] = None
    confidence_level: float  # 0.0 to 1.0
    reasoning: str
    game_phase: str  # "opening", "midgame", "endgame" 