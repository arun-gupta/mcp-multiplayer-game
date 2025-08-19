"""
Scout Agent Module
Observes the current game state and provides intelligence to other agents
"""
import os
from .base_agent import Agent
from models.factory import ModelFactory
from models.registry import model_registry
from schemas.observation import Observation

class ScoutAgent:
    """Scout agent that observes the Tic Tac Toe game state"""
    
    def __init__(self, game_state, model_name: str = "gpt-4"):
        self.game_state = game_state
        self.model_name = model_name
        self.llm = self._create_llm(model_name)
        
        # Create the agent with the LLM
        self.agent = Agent(
            role="Game Scout",
            goal="Observe and analyze the current Tic Tac Toe game state to provide accurate intelligence",
            backstory="""You are an expert game scout specializing in Tic Tac Toe analysis. 
            Your job is to observe the current board state, analyze potential threats and opportunities, 
            and provide clear, actionable intelligence to the strategist. You focus on:
            - Current board layout and available moves
            - Immediate threats (winning opportunities for either player)
            - Blocking opportunities (preventing opponent's win)
            - Strategic positions (center, corners, edges)
            - Game phase analysis (opening, midgame, endgame)
            - Pattern recognition in player moves""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_llm(self, model_name: str):
        """Create LLM instance for the specified model"""
        llm = ModelFactory.create_llm(model_name)
        if llm is None:
            # Fallback to default model
            print(f"Warning: Could not create LLM for {model_name}, falling back to gpt-4")
            llm = ModelFactory.create_llm("gpt-4")
        return llm
    
    def switch_model(self, model_name: str):
        """Switch to a different model"""
        new_llm = self._create_llm(model_name)
        if new_llm:
            self.llm = new_llm
            self.model_name = model_name
            # Update the agent's LLM
            self.agent.llm = new_llm
            # Update game state
            self.game_state.set_agent_model("scout", model_name)
            return True
        return False
    
    def observe_environment(self) -> Observation:
        """Observe the current game state and return an observation"""
        import time
        import psutil
        start_time = time.time()
        
        # Increment MCP message count
        self.game_state.increment_mcp_messages()
        
        # Track message flow pattern
        self.game_state.add_message_flow_pattern("scout_to_strategist")
        
        # Get observation
        observation = self.game_state.get_observation()
        
        # Calculate response time and latency
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.game_state.add_response_time("scout", response_time)
        self.game_state.add_message_latency(response_time)
        
        # Add estimated cost and token usage (GPT-4 pricing)
        estimated_cost = 0.00003  # Rough estimate per message
        estimated_tokens = 150  # Rough estimate per observation
        self.game_state.add_llm_cost("gpt4", estimated_cost)
        self.game_state.add_token_usage("scout", estimated_tokens)
        
        # Update resource utilization
        try:
            cpu_percent = psutil.cpu_percent()
            memory_mb = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB
            self.game_state.update_resource_utilization(cpu_percent, memory_mb)
        except:
            pass  # Ignore if psutil is not available
        
        return observation
    
    def get_agent_info(self) -> dict:
        """Get information about this agent"""
        model_config = model_registry.get_model(self.model_name)
        model_display = model_config.display_name if model_config else self.model_name
        provider = model_config.provider if model_config else "Unknown"
        
        # Determine provider type and icon
        provider_str = str(provider).upper()
        if "OPENAI" in provider_str or "ANTHROPIC" in provider_str:
            provider_type = "☁️ Cloud"
            provider_icon = "☁️"
        elif "OLLAMA" in provider_str:
            provider_type = "🖥️ Local"
            provider_icon = "🖥️"
        else:
            provider_type = "❓ Unknown"
            provider_icon = "❓"
        
        return {
            "name": "Scout Agent",
            "role": "Game Observer",
            "model": model_display,
            "model_name": self.model_name,
            "provider": provider,
            "provider_type": provider_type,
            "provider_icon": provider_icon,
            "description": "Observes board state and analyzes game positions",
            "capabilities": ["Board Analysis", "Threat Detection", "Position Evaluation", "Game State Monitoring"]
        } 