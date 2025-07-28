"""
ActionResult schema for Executor Agent
Defines the results of executed actions and their impact on the game state
"""
from pydantic import BaseModel
from typing import Optional

class MoveResult(BaseModel):
    """Result of executing a single move"""
    move: str  # "rock", "paper", "scissors"
    opponent_move: str  # "rock", "paper", "scissors"
    result: str  # "win", "lose", "draw"
    confidence: float  # How confident the executor was
    execution_time: float  # Time taken to execute (seconds)

class ActionResult(BaseModel):
    """Executor agent's result of executing the plan"""
    round_number: int
    plan_id: str
    move_executed: MoveResult
    strategy_followed: str  # Which strategy was actually used
    success: bool  # Whether the execution was successful
    message: str  # Description of what happened
    score_change: int  # +1 for win, -1 for loss, 0 for draw
    game_continues: bool  # Whether the game should continue 