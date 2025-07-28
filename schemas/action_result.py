"""
ActionResult schema for Executor Agent
Defines the results of executed actions and their impact on the game state
"""
from pydantic import BaseModel
from typing import Optional, List
from .observation import BoardPosition

class MoveResult(BaseModel):
    """The result of executing a move"""
    position: BoardPosition
    move_type: str  # "winning", "blocking", "center", "corner", "edge", "random"
    success: bool
    execution_time: float
    validation_errors: List[str] = []

class ActionResult(BaseModel):
    """Executor agent's result of executing the plan"""
    move_number: int
    plan_id: str
    move_executed: MoveResult
    strategy_followed: str  # Which strategy was actually used
    success: bool  # Whether the execution was successful
    message: str  # Description of what happened
    new_board_state: List[List[str]]  # Updated board after move
    game_over: bool  # Whether the game is over
    winner: Optional[str] = None  # "player", "ai", "draw", or None
    next_player: str  # "player" or "ai" 