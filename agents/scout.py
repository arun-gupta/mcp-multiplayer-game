"""
Scout Agent
Observes the game environment and reports limited view observations
Uses Claude for intelligent observation analysis
"""
from crewai import Agent
from langchain_openai import ChatOpenAI
from schemas.observation import Observation
from game.state import GameState
from typing import Dict, Any
import os


class ScoutAgent:
    """
    Scout Agent responsible for observing the game environment
    Uses Claude to analyze the environment and provide detailed observations
    """
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.visibility_range = 3
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI scout agent with OpenAI GPT-4"""
        # Use OpenAI GPT-4 for intelligent observation
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        return Agent(
            role="Scout",
            goal="Observe the game environment and provide detailed, accurate observations about the current state",
            backstory="""You are an expert scout with keen observational skills. 
            Your job is to analyze the game environment and provide detailed reports about:
            - Player position and health
            - Enemy locations and status
            - Items and resources
            - Terrain and obstacles
            - Potential threats and opportunities
            You must be thorough but concise in your observations.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def observe_environment(self) -> Observation:
        """
        Observe the current game environment and return detailed observations
        """
        player = self.game_state.player_entity
        if not player:
            raise ValueError("No player entity found in game state")
        
        # Get visible tiles from player position
        visible_tiles = self.game_state.game_map.get_visible_tiles(
            player.position, 
            self.visibility_range
        )
        
        # Get entities in range
        enemies_in_range = self.game_state.game_map.get_entities_in_range(
            player.position, 
            self.visibility_range
        )
        enemies_in_range = [e for e in enemies_in_range if e.entity_type == "enemy"]
        
        items_in_range = self.game_state.game_map.get_entities_in_range(
            player.position, 
            self.visibility_range
        )
        items_in_range = [e for e in items_in_range if e.entity_type == "item"]
        
        # Create observation
        observation = Observation(
            scout_position=player.position,
            visible_tiles=visible_tiles,
            visible_entities=enemies_in_range + items_in_range,
            map_size=(self.game_state.game_map.width, self.game_state.game_map.height),
            turn_number=self.game_state.turn_number,
            player_health=player.health or 0,
            player_max_health=player.max_health or 100,
            player_position=player.position,
            enemies_in_range=enemies_in_range,
            items_in_range=items_in_range,
            fog_of_war=True,
            visibility_range=self.visibility_range
        )
        
        # Use the agent to analyze the observation
        analysis = self._analyze_observation(observation)
        
        # Log the observation for MCP protocol tracking
        self._log_observation(observation, analysis)
        
        return observation
    
    def _analyze_observation(self, observation: Observation) -> str:
        """
        Use the scout agent to analyze the observation and provide insights
        """
        # Create a detailed prompt for the scout agent
        prompt = f"""
        Analyze the current game environment and provide strategic insights:
        
        Game State:
        - Turn: {observation.turn_number}
        - Player Health: {observation.player_health}/{observation.player_max_health}
        - Player Position: {observation.player_position}
        - Map Size: {observation.map_size}
        
        Visible Environment:
        - Visible Tiles: {len(observation.visible_tiles)}
        - Enemies in Range: {len(observation.enemies_in_range)}
        - Items in Range: {len(observation.items_in_range)}
        
        Enemies Detected:
        {self._format_entities(observation.enemies_in_range)}
        
        Items Detected:
        {self._format_entities(observation.items_in_range)}
        
        Provide a detailed analysis including:
        1. Immediate threats and their severity
        2. Opportunities for advancement
        3. Strategic positioning recommendations
        4. Resource assessment
        5. Risk level assessment
        """
        
        # Get analysis from the agent
        try:
            analysis = self.agent.execute(prompt)
            return analysis
        except Exception as e:
            # Fallback to basic analysis if agent fails
            return f"Basic analysis: {len(observation.enemies_in_range)} enemies, {len(observation.items_in_range)} items visible"
    
    def _format_entities(self, entities) -> str:
        """Format entities for display in analysis"""
        if not entities:
            return "None"
        
        formatted = []
        for entity in entities:
            formatted.append(f"- {entity.entity_id}: {entity.entity_type} at {entity.position}")
            if entity.health:
                formatted.append(f"  Health: {entity.health}")
            if entity.attack_power:
                formatted.append(f"  Attack: {entity.attack_power}")
        
        return "\n".join(formatted)
    
    def _log_observation(self, observation: Observation, analysis: str):
        """Log the observation for MCP protocol tracking"""
        log_entry = {
            "agent": "Scout",
            "turn": observation.turn_number,
            "observation": observation.dict(),
            "analysis": analysis,
            "timestamp": "now"  # In real implementation, use actual timestamp
        }
        
        # In a real implementation, this would be sent to a logging system
        # For now, we'll just print it
        print(f"[SCOUT] Turn {observation.turn_number} - {len(observation.enemies_in_range)} enemies, {len(observation.items_in_range)} items detected")
        print(f"[SCOUT] Analysis: {analysis[:100]}...")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the scout agent"""
        return {
            "agent_type": "Scout",
            "model": "OpenAI GPT-4",
            "visibility_range": self.visibility_range,
            "capabilities": [
                "Environment observation",
                "Threat detection",
                "Resource identification",
                "Strategic positioning analysis"
            ]
        } 