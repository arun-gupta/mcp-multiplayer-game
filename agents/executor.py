"""
Executor Agent
Executes strategic plans and updates the game state
Uses a small local model for action execution
"""
from crewai import Agent
from langchain_community.llms import Ollama
from schemas.plan import Plan, Action
from schemas.action_result import ActionResult, TurnResult, ActionResultStatus
from game.engine import GameEngine
from game.state import GameState
from typing import List, Dict, Any
import os


class ExecutorAgent:
    """
    Executor Agent responsible for executing plans and updating game state
    Uses a small local model for efficient action execution
    """
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.game_engine = GameEngine(game_state)
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI executor agent with a small local model"""
        # Use a small local model for execution
        llm = Ollama(
            model="llama2:7b",  # Small local model
            temperature=0.1
        )
        
        return Agent(
            role="Executor",
            goal="Execute strategic plans efficiently and accurately, updating the game state accordingly",
            backstory="""You are a precise and efficient executor with excellent attention to detail.
            Your responsibilities include:
            - Executing actions in the correct order and priority
            - Validating action feasibility before execution
            - Handling edge cases and errors gracefully
            - Providing detailed feedback on execution results
            - Maintaining game state consistency
            
            You are methodical and always follow the plan exactly as specified.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def execute_plan(self, plan: Plan) -> TurnResult:
        """
        Execute a complete strategic plan and return the results
        """
        # Validate the plan before execution
        validation_result = self._validate_plan(plan)
        if not validation_result["valid"]:
            return self._create_validation_error_result(plan, validation_result["errors"])
        
        # Execute the plan using the game engine
        turn_result = self.game_engine.execute_turn(plan.actions)
        
        # Use the agent to analyze execution results
        execution_analysis = self._analyze_execution_results(turn_result, plan)
        
        # Log the execution for MCP protocol tracking
        self._log_execution(plan, turn_result, execution_analysis)
        
        return turn_result
    
    def _validate_plan(self, plan: Plan) -> Dict[str, Any]:
        """
        Validate that the plan can be executed with current game state
        """
        errors = []
        
        # Check if plan is for the correct turn
        if plan.turn_number != self.game_state.turn_number:
            errors.append(f"Plan turn number ({plan.turn_number}) doesn't match current turn ({self.game_state.turn_number})")
        
        # Validate each action
        for i, action in enumerate(plan.actions):
            action_validation = self._validate_action(action)
            if not action_validation["valid"]:
                errors.append(f"Action {i+1}: {action_validation['error']}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _validate_action(self, action: Action) -> Dict[str, Any]:
        """
        Validate a single action
        """
        player = self.game_state.player_entity
        if not player:
            return {"valid": False, "error": "No player entity found"}
        
        if action.action_type.value == "move":
            if not action.direction:
                return {"valid": False, "error": "Move action requires direction"}
            
            # Check if move is valid
            from schemas.plan import Direction
            new_pos = self._calculate_new_position(player.position, action.direction)
            if not self.game_state.game_map.is_valid_position(new_pos):
                return {"valid": False, "error": f"Move target position {new_pos} is invalid"}
            
            tile = self.game_state.game_map.get_tile(new_pos)
            if tile and tile.tile_type.value == "wall":
                return {"valid": False, "error": f"Cannot move into wall at {new_pos}"}
            
            if tile and tile.entity and tile.entity.entity_type != "item":
                return {"valid": False, "error": f"Position {new_pos} is occupied by {tile.entity.entity_type}"}
        
        elif action.action_type.value == "attack":
            if not action.target_entity_id and not action.target_position:
                return {"valid": False, "error": "Attack action requires target"}
            
            # Check if target exists
            target_entity = None
            if action.target_entity_id:
                target_entity = self.game_state.game_map.entities.get(action.target_entity_id)
            elif action.target_position:
                entities_at_pos = self.game_state.game_map.get_entities_at_position(action.target_position)
                target_entity = next((e for e in entities_at_pos if e.entity_type == "enemy"), None)
            
            if not target_entity:
                return {"valid": False, "error": "Attack target not found"}
            
            # Check if target is in range
            distance = abs(player.position[0] - target_entity.position[0]) + abs(player.position[1] - target_entity.position[1])
            if distance > 1:
                return {"valid": False, "error": f"Target {target_entity.entity_id} is not in attack range (distance: {distance})"}
        
        elif action.action_type.value == "pickup":
            if not action.target_entity_id and not action.target_position:
                return {"valid": False, "error": "Pickup action requires target"}
            
            # Check if item exists at position
            target_pos = action.target_position or player.position
            entities_at_pos = self.game_state.game_map.get_entities_at_position(target_pos)
            items_at_pos = [e for e in entities_at_pos if e.entity_type == "item"]
            
            if not items_at_pos:
                return {"valid": False, "error": f"No items to pickup at position {target_pos}"}
        
        return {"valid": True, "error": None}
    
    def _calculate_new_position(self, current_pos: tuple[int, int], direction) -> tuple[int, int]:
        """Calculate new position based on direction"""
        x, y = current_pos
        
        if direction.value == "north":
            return (x, y - 1)
        elif direction.value == "south":
            return (x, y + 1)
        elif direction.value == "east":
            return (x + 1, y)
        elif direction.value == "west":
            return (x - 1, y)
        elif direction.value == "northeast":
            return (x + 1, y - 1)
        elif direction.value == "northwest":
            return (x - 1, y - 1)
        elif direction.value == "southeast":
            return (x + 1, y + 1)
        elif direction.value == "southwest":
            return (x - 1, y + 1)
        else:
            return current_pos
    
    def _create_validation_error_result(self, plan: Plan, errors: List[str]) -> TurnResult:
        """
        Create a turn result for validation errors
        """
        failed_action = ActionResult(
            action=Action(action_type="wait", priority=1, reasoning="Validation failed"),
            status=ActionResultStatus.INVALID,
            success=False,
            message=f"Plan validation failed: {'; '.join(errors)}"
        )
        
        return TurnResult(
            turn_number=plan.turn_number,
            plan_id=plan.plan_id,
            actions_executed=[failed_action],
            successful_actions=0,
            failed_actions=1,
            summary=f"Plan execution failed due to validation errors: {'; '.join(errors)}"
        )
    
    def _analyze_execution_results(self, turn_result: TurnResult, plan: Plan) -> str:
        """
        Use the executor agent to analyze execution results
        """
        prompt = f"""
        Analyze the execution results of the strategic plan:
        
        PLAN DETAILS:
        - Plan ID: {plan.plan_id}
        - Turn: {plan.turn_number}
        - Primary Objective: {plan.primary_objective}
        - Expected Outcome: {plan.expected_outcome}
        - Risk Assessment: {plan.risk_assessment}
        
        EXECUTION RESULTS:
        - Actions Executed: {len(turn_result.actions_executed)}
        - Successful Actions: {turn_result.successful_actions}
        - Failed Actions: {turn_result.failed_actions}
        - Total Damage Dealt: {turn_result.total_damage_dealt}
        - Total Damage Taken: {turn_result.total_damage_taken}
        - Items Collected: {len(turn_result.items_collected)}
        - Enemies Defeated: {len(turn_result.enemies_defeated)}
        - Summary: {turn_result.summary}
        
        Provide an analysis of:
        1. How well the plan was executed
        2. What went right and what went wrong
        3. Whether the objectives were achieved
        4. Lessons learned for future planning
        5. Recommendations for next turn
        """
        
        try:
            analysis = self.agent.execute(prompt)
            return analysis
        except Exception as e:
            return f"Basic execution analysis: {turn_result.successful_actions}/{len(turn_result.actions_executed)} actions successful"
    
    def _log_execution(self, plan: Plan, turn_result: TurnResult, analysis: str):
        """Log the execution for MCP protocol tracking"""
        log_entry = {
            "agent": "Executor",
            "turn": plan.turn_number,
            "plan_id": plan.plan_id,
            "execution_results": {
                "actions_executed": len(turn_result.actions_executed),
                "successful_actions": turn_result.successful_actions,
                "failed_actions": turn_result.failed_actions,
                "damage_dealt": turn_result.total_damage_dealt,
                "damage_taken": turn_result.total_damage_taken,
                "items_collected": turn_result.items_collected,
                "enemies_defeated": turn_result.enemies_defeated
            },
            "analysis": analysis,
            "timestamp": "now"  # In real implementation, use actual timestamp
        }
        
        # In a real implementation, this would be sent to a logging system
        # For now, we'll just print it
        print(f"[EXECUTOR] Turn {plan.turn_number} - Executed {len(turn_result.actions_executed)} actions")
        print(f"[EXECUTOR] Success rate: {turn_result.successful_actions}/{len(turn_result.actions_executed)}")
        print(f"[EXECUTOR] Summary: {turn_result.summary}")
        print(f"[EXECUTOR] Analysis: {analysis[:100]}...")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the executor agent"""
        return {
            "agent_type": "Executor",
            "model": "Llama2:7B (Local)",
            "capabilities": [
                "Plan execution",
                "Action validation",
                "Game state updates",
                "Error handling",
                "Execution analysis"
            ]
        } 