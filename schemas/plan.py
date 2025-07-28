"""
Plan schema for Strategist Agent
Defines the strategic plan based on scout's observations
"""
from pydantic import BaseModel
from typing import List, Optional

class Strategy(BaseModel):
    """A single strategic decision"""
    move: str  # "rock", "paper", "scissors"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    expected_outcome: str  # "win", "lose", "draw", "uncertain"

class Plan(BaseModel):
    """Strategist agent's plan for the next move"""
    plan_id: str
    round_number: int
    primary_strategy: Strategy
    alternative_strategies: List[Strategy]
    pattern_analysis: str  # Analysis of opponent's patterns
    risk_assessment: str  # "low", "medium", "high"
    expected_opponent_move: Optional[str] = None
    confidence_level: float  # 0.0 to 1.0
    reasoning: str 