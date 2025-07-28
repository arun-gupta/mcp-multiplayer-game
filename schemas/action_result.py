"""
ActionResult schema for Executor Agent
Defines the results of executed actions and their impact on the game state
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from .plan import Action, ActionType


class ActionResultStatus(str, Enum):
    """Status of action execution"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    INVALID = "invalid"


class ActionResult(BaseModel):
    """
    Result of executing a single action
    """
    action: Action
    status: ActionResultStatus
    success: bool
    message: str
    new_position: Optional[tuple[int, int]] = None
    damage_dealt: Optional[int] = None
    damage_taken: Optional[int] = None
    items_collected: List[str] = []
    enemies_defeated: List[str] = []
    turn_consumed: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": {
                    "action_type": "move",
                    "target_position": [3, 2],
                    "direction": "east",
                    "priority": 1,
                    "reasoning": "Move towards enemy"
                },
                "status": "success",
                "success": True,
                "message": "Successfully moved to position (3,2)",
                "new_position": [3, 2],
                "turn_consumed": True
            }
        }


class TurnResult(BaseModel):
    """
    Complete result of executing a full turn (all actions in a plan)
    """
    turn_number: int
    plan_id: str
    actions_executed: List[ActionResult]
    successful_actions: int
    failed_actions: int
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    items_collected: List[str] = []
    enemies_defeated: List[str] = []
    game_state_changed: bool = True
    summary: str = ""
    
    class Config:
        json_schema_extra = {
            "example": {
                "turn_number": 1,
                "plan_id": "turn_1_plan",
                "actions_executed": [],
                "successful_actions": 1,
                "failed_actions": 0,
                "total_damage_dealt": 0,
                "total_damage_taken": 0,
                "items_collected": [],
                "enemies_defeated": [],
                "game_state_changed": True,
                "summary": "Successfully moved towards enemy position"
            }
        }


class GameStateUpdate(BaseModel):
    """
    Complete game state update after a turn
    """
    turn_number: int
    player_position: tuple[int, int]
    player_health: int
    player_max_health: int
    enemies_remaining: List[Dict[str, Any]]
    items_remaining: List[Dict[str, Any]]
    map_changes: List[Dict[str, Any]] = []
    game_over: bool = False
    victory: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "turn_number": 1,
                "player_position": [3, 2],
                "player_health": 100,
                "player_max_health": 100,
                "enemies_remaining": [
                    {
                        "entity_id": "enemy_1",
                        "position": [4, 2],
                        "health": 50
                    }
                ],
                "items_remaining": [],
                "map_changes": [],
                "game_over": False,
                "victory": False
            }
        } 