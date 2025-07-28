"""
Plan schema for Strategist Agent
Defines the strategic plan based on scout's observations
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum


class ActionType(str, Enum):
    """Types of actions that can be performed"""
    MOVE = "move"
    ATTACK = "attack"
    RETREAT = "retreat"
    PICKUP = "pickup"
    WAIT = "wait"


class Direction(str, Enum):
    """Cardinal directions for movement"""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    NORTHEAST = "northeast"
    NORTHWEST = "northwest"
    SOUTHEAST = "southeast"
    SOUTHWEST = "southwest"


class Action(BaseModel):
    """Represents a single action to be executed"""
    action_type: ActionType
    target_position: Optional[tuple[int, int]] = None
    target_entity_id: Optional[str] = None
    direction: Optional[Direction] = None
    priority: int = 1  # Higher number = higher priority
    reasoning: str = ""  # Why this action was chosen
    
    class Config:
        json_schema_extra = {
            "example": {
                "action_type": "move",
                "target_position": [3, 2],
                "direction": "east",
                "priority": 1,
                "reasoning": "Move towards enemy to engage in combat"
            }
        }


class Plan(BaseModel):
    """
    Strategist Agent's plan based on scout's observations
    Contains prioritized list of actions to achieve objectives
    """
    plan_id: str
    turn_number: int
    primary_objective: str  # Main goal for this turn
    actions: List[Action]
    risk_assessment: str  # Assessment of current situation
    expected_outcome: str  # What should happen after executing plan
    confidence_level: float  # 0.0 to 1.0, how confident in this plan
    alternative_plans: List[str] = []  # Backup strategies if primary fails
    
    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": "turn_1_plan",
                "turn_number": 1,
                "primary_objective": "Engage enemy at position (3,2)",
                "actions": [
                    {
                        "action_type": "move",
                        "target_position": [3, 2],
                        "direction": "east",
                        "priority": 1,
                        "reasoning": "Move towards enemy to engage in combat"
                    }
                ],
                "risk_assessment": "Low risk - enemy is isolated and we have health advantage",
                "expected_outcome": "Player will be in attack range of enemy",
                "confidence_level": 0.85,
                "alternative_plans": ["Retreat if enemy reinforcements arrive"]
            }
        } 