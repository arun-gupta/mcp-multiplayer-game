"""
Game State Module
Manages the overall game state, turn management, and game progression
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from schemas.observation import Entity
from schemas.action_result import TurnResult, GameStateUpdate
from game.map import GameMap
import json
import time


@dataclass
class GameState:
    """
    Complete game state including map, entities, and game metadata
    """
    turn_number: int = 1
    game_map: Optional[GameMap] = None
    player_entity: Optional[Entity] = None
    enemies: List[Entity] = field(default_factory=list)
    items: List[Entity] = field(default_factory=list)
    game_over: bool = False
    victory: bool = False
    turn_history: List[Dict[str, Any]] = field(default_factory=list)
    action_logs: List[Dict[str, Any]] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if self.game_map is None:
            self.game_map = GameMap(5, 5)
    
    def get_player_position(self) -> tuple[int, int]:
        """Get current player position"""
        if self.player_entity:
            return self.player_entity.position
        return (0, 0)
    
    def get_player_health(self) -> int:
        """Get current player health"""
        if self.player_entity:
            return self.player_entity.health or 0
        return 0
    
    def get_player_max_health(self) -> int:
        """Get player max health"""
        if self.player_entity:
            return self.player_entity.max_health or 100
        return 100
    
    def get_enemies(self) -> List[Entity]:
        """Get all active enemies"""
        return [entity for entity in self.game_map.entities.values() 
                if entity.entity_type == "enemy"]
    
    def get_items(self) -> List[Entity]:
        """Get all items on the map"""
        return [entity for entity in self.game_map.entities.values() 
                if entity.entity_type == "item"]
    
    def add_turn_log(self, turn_result: TurnResult):
        """Add a turn result to the history"""
        self.turn_history.append({
            "turn_number": turn_result.turn_number,
            "plan_id": turn_result.plan_id,
            "actions_executed": len(turn_result.actions_executed),
            "successful_actions": turn_result.successful_actions,
            "failed_actions": turn_result.failed_actions,
            "summary": turn_result.summary,
            "timestamp": time.time()
        })
    
    def add_action_log(self, action_log: Dict[str, Any]):
        """Add an action log entry"""
        self.action_logs.append(action_log)
    
    def check_game_over(self) -> bool:
        """Check if the game is over"""
        # Check if player is dead
        if self.get_player_health() <= 0:
            self.game_over = True
            self.victory = False
            return True
        
        # Check if all enemies are defeated
        if len(self.get_enemies()) == 0:
            self.game_over = True
            self.victory = True
            return True
        
        return False
    
    def advance_turn(self):
        """Advance to the next turn"""
        self.turn_number += 1
    
    def get_game_summary(self) -> Dict[str, Any]:
        """Get a summary of the current game state"""
        return {
            "turn_number": self.turn_number,
            "player_position": self.get_player_position(),
            "player_health": self.get_player_health(),
            "player_max_health": self.get_player_max_health(),
            "enemies_remaining": len(self.get_enemies()),
            "items_remaining": len(self.get_items()),
            "game_over": self.game_over,
            "victory": self.victory,
            "total_turns": len(self.turn_history),
            "game_duration": time.time() - self.start_time
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary for serialization"""
        return {
            "turn_number": self.turn_number,
            "game_map": self.game_map.get_map_state() if self.game_map else None,
            "player_entity": self.player_entity.dict() if self.player_entity else None,
            "enemies": [enemy.dict() for enemy in self.get_enemies()],
            "items": [item.dict() for item in self.get_items()],
            "game_over": self.game_over,
            "victory": self.victory,
            "turn_history": self.turn_history,
            "action_logs": self.action_logs,
            "start_time": self.start_time
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load game state from dictionary"""
        self.turn_number = data.get("turn_number", 1)
        self.game_over = data.get("game_over", False)
        self.victory = data.get("victory", False)
        self.turn_history = data.get("turn_history", [])
        self.action_logs = data.get("action_logs", [])
        self.start_time = data.get("start_time", time.time())


class GameStateManager:
    """
    Manages the global game state and provides methods for state updates
    """
    
    def __init__(self):
        self.current_state: Optional[GameState] = None
        self.initialize_new_game()
    
    def initialize_new_game(self, map_width: int = 5, map_height: int = 5):
        """Initialize a new game with default state"""
        from game.map import create_sample_map
        
        self.current_state = GameState()
        self.current_state.game_map = create_sample_map(map_width, map_height)
        
        # Set player entity
        player_entities = self.current_state.game_map.get_entities_by_type("player")
        if player_entities:
            self.current_state.player_entity = player_entities[0]
        
        # Update enemy and item lists
        self.current_state.enemies = self.current_state.get_enemies()
        self.current_state.items = self.current_state.get_items()
    
    def get_current_state(self) -> GameState:
        """Get the current game state"""
        return self.current_state
    
    def update_state_from_turn_result(self, turn_result: TurnResult) -> GameStateUpdate:
        """Update game state based on turn result"""
        if not self.current_state:
            raise ValueError("No active game state")
        
        # Update turn number
        self.current_state.turn_number = turn_result.turn_number
        
        # Add turn to history
        self.current_state.add_turn_log(turn_result)
        
        # Check for game over conditions
        self.current_state.check_game_over()
        
        # Create state update
        state_update = GameStateUpdate(
            turn_number=self.current_state.turn_number,
            player_position=self.current_state.get_player_position(),
            player_health=self.current_state.get_player_health(),
            player_max_health=self.current_state.get_player_max_health(),
            enemies_remaining=[enemy.dict() for enemy in self.current_state.get_enemies()],
            items_remaining=[item.dict() for item in self.current_state.get_items()],
            game_over=self.current_state.game_over,
            victory=self.current_state.victory
        )
        
        return state_update
    
    def get_state_for_api(self) -> Dict[str, Any]:
        """Get formatted state for API response"""
        if not self.current_state:
            return {"error": "No active game"}
        
        return {
            "game_state": self.current_state.get_game_summary(),
            "map_ascii": self.current_state.game_map.to_ascii(),
            "turn_history": self.current_state.turn_history[-10:],  # Last 10 turns
            "action_logs": self.current_state.action_logs[-20:]  # Last 20 actions
        }
    
    def save_game_state(self, filename: str = "game_state.json"):
        """Save current game state to file"""
        if not self.current_state:
            return False
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.current_state.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving game state: {e}")
            return False
    
    def load_game_state(self, filename: str = "game_state.json"):
        """Load game state from file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.current_state = GameState()
            self.current_state.from_dict(data)
            
            # Reconstruct game map
            if data.get("game_map"):
                from game.map import GameMap
                map_data = data["game_map"]
                self.current_state.game_map = GameMap(map_data["width"], map_data["height"])
                
                # Reconstruct entities
                for entity_data in map_data["entities"].values():
                    entity = Entity(**entity_data)
                    self.current_state.game_map.add_entity(entity)
            
            return True
        except Exception as e:
            print(f"Error loading game state: {e}")
            return False 