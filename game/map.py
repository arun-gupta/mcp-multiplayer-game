"""
Game Map Module
Handles the grid-based world representation and tile management
"""
from typing import List, Optional, Tuple, Dict, Any
from schemas.observation import Tile, TileType, Entity
import random


class GameMap:
    """
    Represents the game world as a grid of tiles
    Handles entity placement, visibility, and map operations
    """
    
    def __init__(self, width: int = 5, height: int = 5):
        self.width = width
        self.height = height
        self.tiles: Dict[Tuple[int, int], Tile] = {}
        self.entities: Dict[str, Entity] = {}
        self._initialize_map()
    
    def _initialize_map(self):
        """Initialize the map with empty tiles"""
        for x in range(self.width):
            for y in range(self.height):
                position = (x, y)
                self.tiles[position] = Tile(
                    position=position,
                    tile_type=TileType.EMPTY,
                    entity=None,
                    is_visible=True
                )
    
    def is_valid_position(self, position: Tuple[int, int]) -> bool:
        """Check if a position is within map bounds"""
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_tile(self, position: Tuple[int, int]) -> Optional[Tile]:
        """Get tile at specified position"""
        if self.is_valid_position(position):
            return self.tiles.get(position)
        return None
    
    def set_tile_type(self, position: Tuple[int, int], tile_type: TileType):
        """Set the type of a tile"""
        if self.is_valid_position(position):
            self.tiles[position].tile_type = tile_type
    
    def add_entity(self, entity: Entity) -> bool:
        """Add an entity to the map"""
        if not self.is_valid_position(entity.position):
            return False
        
        # Check if position is already occupied
        if self.tiles[entity.position].entity is not None:
            return False
        
        self.entities[entity.entity_id] = entity
        self.tiles[entity.position].entity = entity
        return True
    
    def remove_entity(self, entity_id: str) -> bool:
        """Remove an entity from the map"""
        if entity_id not in self.entities:
            return False
        
        entity = self.entities[entity_id]
        if self.tiles[entity.position].entity == entity:
            self.tiles[entity.position].entity = None
        
        del self.entities[entity_id]
        return True
    
    def move_entity(self, entity_id: str, new_position: Tuple[int, int]) -> bool:
        """Move an entity to a new position"""
        if entity_id not in self.entities:
            return False
        
        if not self.is_valid_position(new_position):
            return False
        
        # Check if new position is occupied
        if self.tiles[new_position].entity is not None:
            return False
        
        entity = self.entities[entity_id]
        old_position = entity.position
        
        # Remove from old position
        if self.tiles[old_position].entity == entity:
            self.tiles[old_position].entity = None
        
        # Add to new position
        entity.position = new_position
        self.tiles[new_position].entity = entity
        
        return True
    
    def get_entities_at_position(self, position: Tuple[int, int]) -> List[Entity]:
        """Get all entities at a specific position"""
        entities = []
        tile = self.get_tile(position)
        if tile and tile.entity:
            entities.append(tile.entity)
        return entities
    
    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """Get all entities of a specific type"""
        return [entity for entity in self.entities.values() if entity.entity_type == entity_type]
    
    def get_visible_tiles(self, center_position: Tuple[int, int], visibility_range: int = 3) -> List[Tile]:
        """Get tiles visible from a center position within range"""
        visible_tiles = []
        
        for x in range(max(0, center_position[0] - visibility_range), 
                      min(self.width, center_position[0] + visibility_range + 1)):
            for y in range(max(0, center_position[1] - visibility_range), 
                          min(self.height, center_position[1] + visibility_range + 1)):
                position = (x, y)
                tile = self.get_tile(position)
                if tile:
                    # Calculate distance for fog of war effect
                    distance = abs(x - center_position[0]) + abs(y - center_position[1])
                    if distance <= visibility_range:
                        visible_tiles.append(tile)
        
        return visible_tiles
    
    def get_entities_in_range(self, center_position: Tuple[int, int], range_distance: int) -> List[Entity]:
        """Get entities within a certain range of a position"""
        entities_in_range = []
        
        for entity in self.entities.values():
            distance = abs(entity.position[0] - center_position[0]) + abs(entity.position[1] - center_position[1])
            if distance <= range_distance:
                entities_in_range.append(entity)
        
        return entities_in_range
    
    def to_ascii(self) -> str:
        """Convert map to ASCII representation for visualization"""
        ascii_map = []
        
        # Add header with coordinates
        header = "   " + " ".join([str(i) for i in range(self.width)])
        ascii_map.append(header)
        
        for y in range(self.height):
            row = [f"{y:2d} "]
            for x in range(self.width):
                position = (x, y)
                tile = self.get_tile(position)
                
                if tile.entity:
                    if tile.entity.entity_type == "player":
                        row.append("P")
                    elif tile.entity.entity_type == "enemy":
                        row.append("E")
                    elif tile.entity.entity_type == "item":
                        row.append("I")
                    else:
                        row.append("?")
                else:
                    if tile.tile_type == TileType.WALL:
                        row.append("#")
                    elif tile.tile_type == TileType.EMPTY:
                        row.append(".")
                    else:
                        row.append("?")
            
            ascii_map.append("".join(row))
        
        return "\n".join(ascii_map)
    
    def get_map_state(self) -> Dict[str, Any]:
        """Get complete map state for serialization"""
        return {
            "width": self.width,
            "height": self.height,
            "tiles": {str(pos): tile.dict() for pos, tile in self.tiles.items()},
            "entities": {entity_id: entity.dict() for entity_id, entity in self.entities.items()}
        }


def create_sample_map(width: int = 5, height: int = 5) -> GameMap:
    """Create a sample map with player, enemy, and some obstacles"""
    game_map = GameMap(width, height)
    
    # Add some walls
    wall_positions = [(1, 1), (3, 1), (1, 3), (3, 3)]
    for pos in wall_positions:
        if game_map.is_valid_position(pos):
            game_map.set_tile_type(pos, TileType.WALL)
    
    # Add player
    player = Entity(
        entity_id="player",
        entity_type="player",
        position=(0, 0),
        health=100,
        max_health=100,
        attack_power=25
    )
    game_map.add_entity(player)
    
    # Add enemy
    enemy = Entity(
        entity_id="enemy_1",
        entity_type="enemy",
        position=(4, 4),
        health=50,
        max_health=50,
        attack_power=15
    )
    game_map.add_entity(enemy)
    
    # Add an item
    item = Entity(
        entity_id="health_potion",
        entity_type="item",
        position=(2, 2),
        health=None,
        max_health=None,
        attack_power=None
    )
    game_map.add_entity(item)
    
    return game_map 