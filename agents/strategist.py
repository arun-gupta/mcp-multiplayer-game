"""
Strategist Agent
Analyzes scout observations and creates strategic plans
Uses Mistral for strategic planning and decision making
"""
from crewai import Agent
from langchain_anthropic import ChatAnthropic
from schemas.observation import Observation
from schemas.plan import Plan, Action, ActionType, Direction
from typing import List, Dict, Any
import os


class StrategistAgent:
    """
    Strategist Agent responsible for analyzing observations and creating plans
    Uses Mistral for strategic planning and decision making
    """
    
    def __init__(self):
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI strategist agent with Claude"""
        # Use Claude for strategic planning
        llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            temperature=0.3,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        return Agent(
            role="Strategist",
            goal="Analyze scout observations and create optimal strategic plans for the current situation",
            backstory="""You are a brilliant military strategist with decades of experience in tactical planning.
            Your expertise includes:
            - Threat assessment and prioritization
            - Resource optimization
            - Risk management
            - Tactical positioning
            - Combat strategy
            
            You excel at creating detailed, actionable plans that maximize success probability while minimizing risk.
            You always consider multiple scenarios and provide backup strategies.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def create_strategic_plan(self, observation: Observation) -> Plan:
        """
        Analyze the observation and create a strategic plan
        """
        # Create a detailed prompt for strategic analysis
        prompt = self._create_strategic_prompt(observation)
        
        # Get strategic analysis from the agent
        try:
            strategy_analysis = self.agent.execute(prompt)
            plan = self._parse_strategy_to_plan(observation, strategy_analysis)
        except Exception as e:
            # Fallback to basic plan if agent fails
            plan = self._create_fallback_plan(observation)
        
        # Log the plan for MCP protocol tracking
        self._log_plan(plan, observation)
        
        return plan
    
    def _create_strategic_prompt(self, observation: Observation) -> str:
        """Create a detailed prompt for strategic analysis"""
        return f"""
        Analyze the current game situation and create a strategic plan:
        
        CURRENT SITUATION:
        - Turn: {observation.turn_number}
        - Player Health: {observation.player_health}/{observation.player_max_health}
        - Player Position: {observation.player_position}
        - Map Size: {observation.map_size}
        
        ENEMIES DETECTED ({len(observation.enemies_in_range)}):
        {self._format_enemies_for_strategy(observation.enemies_in_range)}
        
        ITEMS AVAILABLE ({len(observation.items_in_range)}):
        {self._format_items_for_strategy(observation.items_in_range)}
        
        VISIBLE TERRAIN:
        - Visible tiles: {len(observation.visible_tiles)}
        - Fog of war: {observation.fog_of_war}
        - Visibility range: {observation.visibility_range}
        
        STRATEGIC ANALYSIS REQUIRED:
        1. Assess immediate threats and their priority
        2. Identify opportunities (items, positioning, etc.)
        3. Determine optimal action sequence
        4. Calculate risk vs reward for each action
        5. Consider multiple scenarios and contingencies
        
        Create a detailed strategic plan including:
        - Primary objective for this turn
        - Prioritized list of actions
        - Risk assessment
        - Expected outcomes
        - Alternative strategies if primary plan fails
        
        Format your response as a structured plan with clear action items.
        """
    
    def _format_enemies_for_strategy(self, enemies) -> str:
        """Format enemies for strategic analysis"""
        if not enemies:
            return "No enemies detected"
        
        formatted = []
        for enemy in enemies:
            distance = abs(enemy.position[0] - (0, 0)[0]) + abs(enemy.position[1] - (0, 0)[1])
            formatted.append(f"- {enemy.entity_id}: {enemy.entity_type} at {enemy.position} (distance: {distance})")
            if enemy.health:
                formatted.append(f"  Health: {enemy.health}")
            if enemy.attack_power:
                formatted.append(f"  Attack Power: {enemy.attack_power}")
        
        return "\n".join(formatted)
    
    def _format_items_for_strategy(self, items) -> str:
        """Format items for strategic analysis"""
        if not items:
            return "No items available"
        
        formatted = []
        for item in items:
            distance = abs(item.position[0] - (0, 0)[0]) + abs(item.position[1] - (0, 0)[1])
            formatted.append(f"- {item.entity_id}: {item.entity_type} at {item.position} (distance: {distance})")
        
        return "\n".join(formatted)
    
    def _parse_strategy_to_plan(self, observation: Observation, strategy_analysis: str) -> Plan:
        """
        Parse the strategy analysis into a structured plan
        This is a simplified parser - in a real implementation, you'd want more sophisticated parsing
        """
        # Create a basic plan based on the current situation
        actions = []
        
        # Check if there are enemies in range
        if observation.enemies_in_range:
            # Prioritize attacking if enemies are close
            for enemy in observation.enemies_in_range:
                distance = abs(enemy.position[0] - observation.player_position[0]) + abs(enemy.position[1] - observation.player_position[1])
                if distance <= 1:  # In attack range
                    actions.append(Action(
                        action_type=ActionType.ATTACK,
                        target_entity_id=enemy.entity_id,
                        target_position=enemy.position,
                        priority=1,
                        reasoning=f"Attack enemy {enemy.entity_id} at close range"
                    ))
                else:
                    # Move towards enemy
                    direction = self._calculate_direction_to_target(observation.player_position, enemy.position)
                    actions.append(Action(
                        action_type=ActionType.MOVE,
                        direction=direction,
                        target_position=enemy.position,
                        priority=2,
                        reasoning=f"Move towards enemy {enemy.entity_id}"
                    ))
        
        # Check for items to collect
        if observation.items_in_range:
            for item in observation.items_in_range:
                distance = abs(item.position[0] - observation.player_position[0]) + abs(item.position[1] - observation.player_position[1])
                if distance == 0:  # On same tile
                    actions.append(Action(
                        action_type=ActionType.PICKUP,
                        target_entity_id=item.entity_id,
                        target_position=item.position,
                        priority=3,
                        reasoning=f"Pick up {item.entity_id}"
                    ))
                else:
                    # Move towards item
                    direction = self._calculate_direction_to_target(observation.player_position, item.position)
                    actions.append(Action(
                        action_type=ActionType.MOVE,
                        direction=direction,
                        target_position=item.position,
                        priority=4,
                        reasoning=f"Move towards {item.entity_id}"
                    ))
        
        # If no specific actions, wait
        if not actions:
            actions.append(Action(
                action_type=ActionType.WAIT,
                priority=5,
                reasoning="No immediate actions required"
            ))
        
        # Create the plan
        primary_objective = self._determine_primary_objective(observation, actions)
        risk_assessment = self._assess_risk(observation, actions)
        expected_outcome = self._predict_outcome(observation, actions)
        
        return Plan(
            plan_id=f"turn_{observation.turn_number}_plan",
            turn_number=observation.turn_number,
            primary_objective=primary_objective,
            actions=actions,
            risk_assessment=risk_assessment,
            expected_outcome=expected_outcome,
            confidence_level=0.8,
            alternative_plans=["Retreat if health drops below 50%", "Focus on item collection if enemies are too strong"]
        )
    
    def _create_fallback_plan(self, observation: Observation) -> Plan:
        """Create a basic fallback plan if agent analysis fails"""
        actions = [Action(
            action_type=ActionType.WAIT,
            priority=1,
            reasoning="Fallback plan - waiting for better intelligence"
        )]
        
        return Plan(
            plan_id=f"turn_{observation.turn_number}_fallback_plan",
            turn_number=observation.turn_number,
            primary_objective="Maintain current position and assess situation",
            actions=actions,
            risk_assessment="Low risk - defensive stance",
            expected_outcome="No immediate changes to game state",
            confidence_level=0.5,
            alternative_plans=["Move randomly if threatened"]
        )
    
    def _calculate_direction_to_target(self, current_pos: tuple[int, int], target_pos: tuple[int, int]) -> Direction:
        """Calculate the direction to move towards a target"""
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]
        
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
    
    def _determine_primary_objective(self, observation: Observation, actions: List[Action]) -> str:
        """Determine the primary objective based on the situation"""
        if any(action.action_type == ActionType.ATTACK for action in actions):
            return "Engage and defeat enemies"
        elif any(action.action_type == ActionType.PICKUP for action in actions):
            return "Collect valuable items"
        elif any(action.action_type == ActionType.MOVE for action in actions):
            return "Advance towards objectives"
        else:
            return "Maintain defensive position"
    
    def _assess_risk(self, observation: Observation, actions: List[Action]) -> str:
        """Assess the risk level of the planned actions"""
        if observation.player_health < 50:
            return "High risk - low health"
        elif len(observation.enemies_in_range) > 2:
            return "High risk - multiple enemies"
        elif len(observation.enemies_in_range) == 1:
            return "Medium risk - single enemy"
        else:
            return "Low risk - no immediate threats"
    
    def _predict_outcome(self, observation: Observation, actions: List[Action]) -> str:
        """Predict the expected outcome of the planned actions"""
        if any(action.action_type == ActionType.ATTACK for action in actions):
            return "Engage in combat with enemies"
        elif any(action.action_type == ActionType.PICKUP for action in actions):
            return "Collect items to improve capabilities"
        elif any(action.action_type == ActionType.MOVE for action in actions):
            return "Reposition for better tactical advantage"
        else:
            return "Maintain current position"
    
    def _log_plan(self, plan: Plan, observation: Observation):
        """Log the plan for MCP protocol tracking"""
        log_entry = {
            "agent": "Strategist",
            "turn": observation.turn_number,
            "plan": plan.dict(),
            "observation_summary": {
                "enemies": len(observation.enemies_in_range),
                "items": len(observation.items_in_range),
                "player_health": observation.player_health
            },
            "timestamp": "now"  # In real implementation, use actual timestamp
        }
        
        # In a real implementation, this would be sent to a logging system
        # For now, we'll just print it
        print(f"[STRATEGIST] Turn {observation.turn_number} - Created plan with {len(plan.actions)} actions")
        print(f"[STRATEGIST] Primary objective: {plan.primary_objective}")
        print(f"[STRATEGIST] Risk assessment: {plan.risk_assessment}")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the strategist agent"""
        return {
            "agent_type": "Strategist",
            "model": "Claude 3 Sonnet (Anthropic)",
            "capabilities": [
                "Strategic analysis",
                "Threat assessment",
                "Resource optimization",
                "Risk management",
                "Tactical planning"
            ]
        } 