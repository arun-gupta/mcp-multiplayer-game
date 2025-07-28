"""
Game Engine Module
Handles game mechanics, combat, movement, and action execution
"""
from typing import List, Optional, Tuple, Dict, Any
from schemas.observation import Entity, TileType
from schemas.plan import Action, ActionType, Direction
from schemas.action_result import ActionResult, ActionResultStatus, TurnResult
from game.map import GameMap
from game.state import GameState
import random


class GameEngine:
    """
    Core game engine that handles all game mechanics and action execution
    """
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.game_map = game_state.game_map
    
    def execute_action(self, action: Action) -> ActionResult:
        """
        Execute a single action and return the result
        """
        if action.action_type == ActionType.MOVE:
            return self._execute_move_action(action)
        elif action.action_type == ActionType.ATTACK:
            return self._execute_attack_action(action)
        elif action.action_type == ActionType.PICKUP:
            return self._execute_pickup_action(action)
        elif action.action_type == ActionType.RETREAT:
            return self._execute_retreat_action(action)
        elif action.action_type == ActionType.WAIT:
            return self._execute_wait_action(action)
        else:
            return ActionResult(
                action=action,
                status=ActionResultStatus.INVALID,
                success=False,
                message=f"Unknown action type: {action.action_type}"
            )
    
    def _execute_move_action(self, action: Action) -> ActionResult:
        """Execute a move action"""
        player = self.game_state.player_entity
        if not player:
            return ActionResult(
                action=action,
                status=ActionResultStatus.FAILED,
                success=False,
                message="No player entity found"
            )
        
        # Calculate new position
        current_pos = player.position
        new_pos = self._calculate_new_position(current_pos, action.direction)
        
        # Validate move
        if not self._is_valid_move(new_pos):
            return ActionResult(
                action=action,
                status=ActionResultStatus.FAILED,
                success=False,
                message=f"Cannot move to position {new_pos} - invalid or occupied"
            )
        
        # Execute move
        success = self.game_map.move_entity("player", new_pos)
        if success:
            return ActionResult(
                action=action,
                status=ActionResultStatus.SUCCESS,
                success=True,
                message=f"Successfully moved to position {new_pos}",
                new_position=new_pos
            )
        else:
            return ActionResult(
                action=action,
                status=ActionResultStatus.FAILED,
                success=False,
                message="Failed to move entity"
            )
    
    def _execute_attack_action(self, action: Action) -> ActionResult:
        """Execute an attack action"""
        player = self.game_state.player_entity
        if not player:
            return ActionResult(
                action=action,
                status=ActionResultStatus.FAILED,
                success=False,
                message="No player entity found"
            )
        
        # Find target entity
        target_entity = None
        if action.target_entity_id:
            target_entity = self.game_map.entities.get(action.target_entity_id)
        elif action.target_position:
            entities_at_pos = self.game_map.get_entities_at_position(action.target_position)
            for entity in entities_at_pos:
                if entity.entity_type == "enemy":
                    target_entity = entity
                    break
        
        if not target_entity:
            return ActionResult(
                action=action,
                status=ActionResultStatus.FAILED,
                success=False,
                message="No valid target found for attack"
            )
        
        # Check if target is in range
        if not self._is_in_attack_range(player.position, target_entity.position):
            return ActionResult(
                action=action,
                status=ActionResultStatus.FAILED,
                success=False,
                message="Target is not in attack range"
            )
        
        # Calculate damage
        damage = self._calculate_damage(player.attack_power or 0)
        
        # Apply damage
        if target_entity.health:
            target_entity.health = max(0, target_entity.health - damage)
        
        # Check if target is defeated
        enemies_defeated = []
        if target_entity.health and target_entity.health <= 0:
            self.game_map.remove_entity(target_entity.entity_id)
            enemies_defeated.append(target_entity.entity_id)
        
        return ActionResult(
            action=action,
            status=ActionResultStatus.SUCCESS,
            success=True,
            message=f"Successfully attacked {target_entity.entity_id} for {damage} damage",
            damage_dealt=damage,
            enemies_defeated=enemies_defeated
        )
    
    def _execute_pickup_action(self, action: Action) -> ActionResult:
        """Execute a pickup action"""
        player = self.game_state.player_entity
        if not player:
            return ActionResult(
                action=action,
                status=ActionResultStatus.FAILED,
                success=False,
                message="No player entity found"
            )
        
        # Find item at player position
        entities_at_pos = self.game_map.get_entities_at_position(player.position)
        items_at_pos = [e for e in entities_at_pos if e.entity_type == "item"]
        
        if not items_at_pos:
            return ActionResult(
                action=action,
                status=ActionResultStatus.FAILED,
                success=False,
                message="No items to pickup at current position"
            )
        
        # Pickup first item
        item = items_at_pos[0]
        self.game_map.remove_entity(item.entity_id)
        
        # Apply item effects (simplified)
        items_collected = [item.entity_id]
        
        return ActionResult(
            action=action,
            status=ActionResultStatus.SUCCESS,
            success=True,
            message=f"Successfully picked up {item.entity_id}",
            items_collected=items_collected
        )
    
    def _execute_retreat_action(self, action: Action) -> ActionResult:
        """Execute a retreat action (move away from enemies)"""
        player = self.game_state.player_entity
        if not player:
            return ActionResult(
                action=action,
                status=ActionResultStatus.FAILED,
                success=False,
                message="No player entity found"
            )
        
        # Find safe direction (away from enemies)
        safe_direction = self._find_safe_direction(player.position)
        if not safe_direction:
            return ActionResult(
                action=action,
                status=ActionResultStatus.FAILED,
                success=False,
                message="No safe direction to retreat"
            )
        
        # Create move action and execute it
        move_action = Action(
            action_type=ActionType.MOVE,
            direction=safe_direction,
            reasoning="Retreating from enemies"
        )
        
        return self._execute_move_action(move_action)
    
    def _execute_wait_action(self, action: Action) -> ActionResult:
        """Execute a wait action (do nothing)"""
        return ActionResult(
            action=action,
            status=ActionResultStatus.SUCCESS,
            success=True,
            message="Waited for one turn",
            turn_consumed=True
        )
    
    def _calculate_new_position(self, current_pos: Tuple[int, int], direction: Direction) -> Tuple[int, int]:
        """Calculate new position based on direction"""
        x, y = current_pos
        
        if direction == Direction.NORTH:
            return (x, y - 1)
        elif direction == Direction.SOUTH:
            return (x, y + 1)
        elif direction == Direction.EAST:
            return (x + 1, y)
        elif direction == Direction.WEST:
            return (x - 1, y)
        elif direction == Direction.NORTHEAST:
            return (x + 1, y - 1)
        elif direction == Direction.NORTHWEST:
            return (x - 1, y - 1)
        elif direction == Direction.SOUTHEAST:
            return (x + 1, y + 1)
        elif direction == Direction.SOUTHWEST:
            return (x - 1, y + 1)
        else:
            return current_pos
    
    def _is_valid_move(self, position: Tuple[int, int]) -> bool:
        """Check if a move to a position is valid"""
        if not self.game_map.is_valid_position(position):
            return False
        
        tile = self.game_map.get_tile(position)
        if not tile:
            return False
        
        # Check if tile is walkable
        if tile.tile_type == TileType.WALL:
            return False
        
        # Check if tile is occupied by non-item entity
        if tile.entity and tile.entity.entity_type != "item":
            return False
        
        return True
    
    def _is_in_attack_range(self, attacker_pos: Tuple[int, int], target_pos: Tuple[int, int], range_distance: int = 1) -> bool:
        """Check if target is in attack range"""
        distance = abs(attacker_pos[0] - target_pos[0]) + abs(attacker_pos[1] - target_pos[1])
        return distance <= range_distance
    
    def _calculate_damage(self, base_damage: int, variance: float = 0.2) -> int:
        """Calculate damage with some variance"""
        variance_amount = int(base_damage * variance)
        damage = base_damage + random.randint(-variance_amount, variance_amount)
        return max(1, damage)  # Minimum 1 damage
    
    def _find_safe_direction(self, current_pos: Tuple[int, int]) -> Optional[Direction]:
        """Find a safe direction to retreat (away from enemies)"""
        enemies = self.game_state.get_enemies()
        if not enemies:
            return None
        
        # Calculate direction away from nearest enemy
        nearest_enemy = min(enemies, key=lambda e: abs(e.position[0] - current_pos[0]) + abs(e.position[1] - current_pos[1]))
        
        dx = current_pos[0] - nearest_enemy.position[0]
        dy = current_pos[1] - nearest_enemy.position[1]
        
        # Determine primary direction
        if abs(dx) > abs(dy):
            if dx > 0:
                return Direction.EAST
            else:
                return Direction.WEST
        else:
            if dy > 0:
                return Direction.SOUTH
            else:
                return Direction.NORTH
    
    def execute_turn(self, actions: List[Action]) -> TurnResult:
        """
        Execute a complete turn with multiple actions
        """
        results = []
        successful_actions = 0
        failed_actions = 0
        total_damage_dealt = 0
        total_damage_taken = 0
        items_collected = []
        enemies_defeated = []
        
        # Sort actions by priority (higher priority first)
        sorted_actions = sorted(actions, key=lambda a: a.priority, reverse=True)
        
        for action in sorted_actions:
            result = self.execute_action(action)
            results.append(result)
            
            if result.success:
                successful_actions += 1
            else:
                failed_actions += 1
            
            # Aggregate results
            if result.damage_dealt:
                total_damage_dealt += result.damage_dealt
            if result.damage_taken:
                total_damage_taken += result.damage_taken
            if result.items_collected:
                items_collected.extend(result.items_collected)
            if result.enemies_defeated:
                enemies_defeated.extend(result.enemies_defeated)
        
        # Create turn summary
        summary = f"Executed {len(actions)} actions: {successful_actions} successful, {failed_actions} failed"
        if total_damage_dealt > 0:
            summary += f". Dealt {total_damage_dealt} damage"
        if enemies_defeated:
            summary += f". Defeated {len(enemies_defeated)} enemies"
        if items_collected:
            summary += f". Collected {len(items_collected)} items"
        
        return TurnResult(
            turn_number=self.game_state.turn_number,
            plan_id=f"turn_{self.game_state.turn_number}_plan",
            actions_executed=results,
            successful_actions=successful_actions,
            failed_actions=failed_actions,
            total_damage_dealt=total_damage_dealt,
            total_damage_taken=total_damage_taken,
            items_collected=items_collected,
            enemies_defeated=enemies_defeated,
            summary=summary
        ) 