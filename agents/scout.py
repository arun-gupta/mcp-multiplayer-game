"""
Scout Agent Module
Observes the current game state and provides intelligence to other agents
"""
import os
from crewai import Agent
from langchain_openai import ChatOpenAI
from schemas.observation import Observation

class ScoutAgent:
    """Scout agent that observes the Tic Tac Toe game state"""
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
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
    
    def observe_environment(self) -> Observation:
        """Observe the current game state and return an observation"""
        import time
        start_time = time.time()
        
        # Increment MCP message count
        self.game_state.increment_mcp_messages()
        
        # Get observation
        observation = self.game_state.get_observation()
        
        # Calculate response time
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.game_state.add_response_time("scout", response_time)
        
        # Add estimated cost (GPT-4 pricing)
        estimated_cost = 0.00003  # Rough estimate per message
        self.game_state.add_llm_cost("gpt4", estimated_cost)
        
        return observation
    
    def get_agent_info(self) -> dict:
        """Get information about this agent"""
        return {
            "name": "Scout Agent",
            "role": "Game Observer",
            "model": "OpenAI GPT-4",
            "description": "Observes board state and analyzes game positions",
            "capabilities": ["Board Analysis", "Threat Detection", "Position Evaluation", "Game State Monitoring"]
        } 