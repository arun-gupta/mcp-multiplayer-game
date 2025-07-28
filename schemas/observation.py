"""
Observation schema for Scout Agent
Defines what the scout can observe and report back to the strategist
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum


class TileType(str, Enum):
    """Types of tiles in the game world"""
    EMPTY = "empty"
    WALL = "wall"
    PLAYER = "player"
    ENEMY = "enemy"
    ITEM = "item"


class Entity(BaseModel):
    """Represents an entity (player, enemy, item) on the map"""
    entity_id: str
    entity_type: str  # "player", "enemy", "item"
    position: tuple[int, int]
    health: Optional[int] = None
    max_health: Optional[int] = None
    attack_power: Optional[int] = None
    is_visible: bool = True


class Tile(BaseModel):
    """Represents a single tile in the game world"""
    position: tuple[int, int]
    tile_type: TileType
    entity: Optional[Entity] = None
    is_visible: bool = True


class Observation(BaseModel):
    """
    Scout Agent's observation of the game world
    Contains limited view based on scout's position and visibility range
    """
    scout_position: tuple[int, int]
    visible_tiles: List[Tile]
    visible_entities: List[Entity]
    map_size: tuple[int, int]
    turn_number: int
    player_health: int
    player_max_health: int
    player_position: tuple[int, int]
    enemies_in_range: List[Entity]
    items_in_range: List[Entity]
    fog_of_war: bool = True  # Whether scout has limited visibility
    visibility_range: int = 3  # How far scout can see
    
    class Config:
        json_schema_extra = {
            "example": {
                "scout_position": [2, 2],
                "visible_tiles": [],
                "visible_entities": [],
                "map_size": [5, 5],
                "turn_number": 1,
                "player_health": 100,
                "player_max_health": 100,
                "player_position": [2, 2],
                "enemies_in_range": [],
                "items_in_range": [],
                "fog_of_war": True,
                "visibility_range": 3
            }
        } 