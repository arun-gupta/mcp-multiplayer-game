"""
Scout Agent Module
Observes the current game state and provides intelligence to other agents
"""
import os
from crewai import Agent
from langchain_openai import ChatOpenAI
from schemas.observation import Observation
from game.state import RPSGameState

class ScoutAgent:
    """Scout agent that observes the current game state"""
    
    def __init__(self, game_state: RPSGameState):
        self.game_state = game_state
        
        # Initialize LLM (OpenAI GPT-4)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=api_key
        )
        
        # Create CrewAI agent
        self.agent = Agent(
            role="Game Scout",
            goal="Observe and analyze the current Rock-Paper-Scissors game state to provide accurate intelligence",
            backstory="""You are an expert game scout specializing in Rock-Paper-Scissors tournaments. 
            Your job is to observe the current game state, analyze patterns in the opponent's moves, 
            and provide clear, actionable intelligence to the strategist. You focus on:
            - Current score and game progress
            - Opponent's move patterns and tendencies
            - Recent game history and trends
            - Identifying any predictable behaviors""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def observe_environment(self) -> Observation:
        """Observe the current game state and return structured observation"""
        try:
            # Get current observation from game state
            observation = self.game_state.get_observation()
            
            # Use the agent to enhance the observation with analysis
            task_description = f"""
            Analyze the current Rock-Paper-Scissors game state:
            
            Current Round: {observation.current_round}
            Player Score: {observation.player_score}
            Opponent Score: {observation.opponent_score}
            Total Rounds Played: {observation.total_rounds_played}
            Current Streak: {observation.current_streak}
            
            Recent Opponent Moves: {observation.last_opponent_moves}
            Game History: {[f"R{h.round_number}: {h.player_move} vs {h.opponent_move} ({h.result})" for h in observation.game_history[-3:]]}
            
            Provide a clear analysis of the current situation and any patterns you observe.
            """
            
            # The agent can provide additional insights, but we return the structured observation
            # In a real implementation, you might use the agent's analysis to enhance the observation
            
            return observation
            
        except Exception as e:
            print(f"Error in ScoutAgent.observe_environment: {e}")
            # Return a basic observation if there's an error
            return self.game_state.get_observation()
    
    def get_agent_info(self) -> dict:
        """Get information about this agent"""
        return {
            "name": "Scout Agent",
            "role": "Game Observer",
            "model": "OpenAI GPT-4",
            "description": "Observes game state and analyzes opponent patterns",
            "capabilities": ["Pattern Recognition", "Game State Analysis", "Intelligence Gathering"]
        } 