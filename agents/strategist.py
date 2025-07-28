"""
Strategist Agent Module
Analyzes scout observations and creates strategic plans for Rock-Paper-Scissors
"""
import os
from crewai import Agent
from langchain_anthropic import ChatAnthropic
from schemas.observation import Observation
from schemas.plan import Plan, Strategy

class StrategistAgent:
    """Strategist agent that creates strategic plans based on observations"""
    
    def __init__(self):
        # Initialize LLM (Claude 3 Sonnet)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            temperature=0.2,
            api_key=api_key
        )
        
        # Create CrewAI agent
        self.agent = Agent(
            role="Game Strategist",
            goal="Analyze game observations and create optimal strategies for Rock-Paper-Scissors",
            backstory="""You are an expert Rock-Paper-Scissors strategist with deep understanding of:
            - Pattern recognition and opponent behavior analysis
            - Probability and game theory
            - Psychological aspects of the game
            - Strategic timing and move selection
            
            Your job is to analyze the scout's observations and create the best possible strategy
            for the next move, considering the opponent's patterns, current score, and game context.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_strategic_plan(self, observation: Observation) -> Plan:
        """Create a strategic plan based on the scout's observation"""
        try:
            # Analyze opponent patterns
            pattern_analysis = self._analyze_opponent_patterns(observation)
            
            # Create primary strategy
            primary_strategy = self._create_primary_strategy(observation, pattern_analysis)
            
            # Create alternative strategies
            alternative_strategies = self._create_alternative_strategies(observation, pattern_analysis)
            
            # Assess risk level
            risk_assessment = self._assess_risk(observation)
            
            # Create the plan
            plan = Plan(
                plan_id=f"round_{observation.current_round}_plan",
                round_number=observation.current_round,
                primary_strategy=primary_strategy,
                alternative_strategies=alternative_strategies,
                pattern_analysis=pattern_analysis,
                risk_assessment=risk_assessment,
                expected_opponent_move=self._predict_opponent_move(observation),
                confidence_level=self._calculate_confidence(observation),
                reasoning=self._generate_reasoning(observation, pattern_analysis)
            )
            
            return plan
            
        except Exception as e:
            print(f"Error in StrategistAgent.create_strategic_plan: {e}")
            # Return a fallback plan
            return self._create_fallback_plan(observation)
    
    def _analyze_opponent_patterns(self, observation: Observation) -> str:
        """Analyze patterns in opponent's moves"""
        if not observation.last_opponent_moves:
            return "No opponent history available"
        
        moves = observation.last_opponent_moves
        rock_count = moves.count("rock")
        paper_count = moves.count("paper")
        scissors_count = moves.count("scissors")
        
        total = len(moves)
        if total == 0:
            return "No moves to analyze"
        
        analysis = f"Opponent's last {total} moves: "
        analysis += f"Rock: {rock_count}/{total} ({rock_count/total*100:.1f}%), "
        analysis += f"Paper: {paper_count}/{total} ({paper_count/total*100:.1f}%), "
        analysis += f"Scissors: {scissors_count}/{total} ({scissors_count/total*100:.1f}%)"
        
        # Identify patterns
        if rock_count > total * 0.6:
            analysis += " - HEAVY ROCK BIAS"
        elif paper_count > total * 0.6:
            analysis += " - HEAVY PAPER BIAS"
        elif scissors_count > total * 0.6:
            analysis += " - HEAVY SCISSORS BIAS"
        elif len(set(moves)) == 1:
            analysis += " - REPEATING SAME MOVE"
        elif len(set(moves)) == 3:
            analysis += " - RANDOM PATTERN"
        
        return analysis
    
    def _create_primary_strategy(self, observation: Observation, pattern_analysis: str) -> Strategy:
        """Create the primary strategy based on analysis"""
        # Simple strategy logic
        if "HEAVY ROCK BIAS" in pattern_analysis:
            move = "paper"
            reasoning = "Opponent heavily favors rock, paper will win"
            confidence = 0.8
        elif "HEAVY PAPER BIAS" in pattern_analysis:
            move = "scissors"
            reasoning = "Opponent heavily favors paper, scissors will win"
            confidence = 0.8
        elif "HEAVY SCISSORS BIAS" in pattern_analysis:
            move = "rock"
            reasoning = "Opponent heavily favors scissors, rock will win"
            confidence = 0.8
        elif "REPEATING SAME MOVE" in pattern_analysis:
            last_move = observation.last_opponent_moves[-1] if observation.last_opponent_moves else "rock"
            if last_move == "rock":
                move = "paper"
            elif last_move == "paper":
                move = "scissors"
            else:
                move = "rock"
            reasoning = f"Opponent repeating {last_move}, counter with {move}"
            confidence = 0.7
        else:
            # Default to rock (most common first move)
            move = "rock"
            reasoning = "No clear pattern, defaulting to rock"
            confidence = 0.5
        
        return Strategy(
            move=move,
            confidence=confidence,
            reasoning=reasoning,
            expected_outcome="win" if confidence > 0.6 else "uncertain"
        )
    
    def _create_alternative_strategies(self, observation: Observation, pattern_analysis: str) -> list[Strategy]:
        """Create alternative strategies as backups"""
        alternatives = []
        
        # Alternative 1: Counter the most recent move
        if observation.last_opponent_moves:
            last_move = observation.last_opponent_moves[-1]
            if last_move == "rock":
                alt_move = "paper"
            elif last_move == "paper":
                alt_move = "scissors"
            else:
                alt_move = "rock"
            
            alternatives.append(Strategy(
                move=alt_move,
                confidence=0.6,
                reasoning=f"Counter opponent's last move ({last_move})",
                expected_outcome="win"
            ))
        
        # Alternative 2: Random move
        alternatives.append(Strategy(
            move="scissors",
            confidence=0.3,
            reasoning="Random move to break patterns",
            expected_outcome="uncertain"
        ))
        
        return alternatives
    
    def _assess_risk(self, observation: Observation) -> str:
        """Assess the risk level of the current situation"""
        if observation.player_score > observation.opponent_score + 2:
            return "low"  # We're ahead
        elif observation.opponent_score > observation.player_score + 2:
            return "high"  # We're behind
        else:
            return "medium"  # Close game
    
    def _predict_opponent_move(self, observation: Observation) -> str:
        """Predict what the opponent will do next"""
        if not observation.last_opponent_moves:
            return "rock"  # Most common first move
        
        # Simple prediction based on most common recent move
        moves = observation.last_opponent_moves
        rock_count = moves.count("rock")
        paper_count = moves.count("paper")
        scissors_count = moves.count("scissors")
        
        if rock_count >= paper_count and rock_count >= scissors_count:
            return "rock"
        elif paper_count >= scissors_count:
            return "paper"
        else:
            return "scissors"
    
    def _calculate_confidence(self, observation: Observation) -> float:
        """Calculate confidence level in the strategy"""
        if not observation.last_opponent_moves:
            return 0.3  # Low confidence with no history
        
        # Higher confidence if we have more data
        history_length = len(observation.last_opponent_moves)
        base_confidence = min(0.8, 0.3 + (history_length * 0.1))
        
        # Adjust based on pattern strength
        moves = observation.last_opponent_moves
        if len(set(moves)) == 1:
            base_confidence += 0.2  # Strong pattern
        elif len(set(moves)) == 2:
            base_confidence += 0.1  # Moderate pattern
        
        return min(1.0, base_confidence)
    
    def _generate_reasoning(self, observation: Observation, pattern_analysis: str) -> str:
        """Generate reasoning for the strategy"""
        reasoning = f"Round {observation.current_round} strategy: "
        reasoning += f"Score is {observation.player_score}-{observation.opponent_score}. "
        reasoning += f"Pattern analysis: {pattern_analysis}. "
        
        if observation.current_streak == "winning":
            reasoning += "We're on a winning streak, maintain momentum. "
        elif observation.current_streak == "losing":
            reasoning += "We're on a losing streak, need to change approach. "
        
        reasoning += f"Confidence level: {self._calculate_confidence(observation):.1f}"
        
        return reasoning
    
    def _create_fallback_plan(self, observation: Observation) -> Plan:
        """Create a fallback plan if strategy creation fails"""
        return Plan(
            plan_id=f"round_{observation.current_round}_fallback",
            round_number=observation.current_round,
            primary_strategy=Strategy(
                move="rock",
                confidence=0.3,
                reasoning="Fallback strategy - default to rock",
                expected_outcome="uncertain"
            ),
            alternative_strategies=[],
            pattern_analysis="Fallback - no analysis available",
            risk_assessment="medium",
            confidence_level=0.3,
            reasoning="Fallback plan due to error in strategy creation"
        )
    
    def get_agent_info(self) -> dict:
        """Get information about this agent"""
        return {
            "name": "Strategist Agent",
            "role": "Strategy Creator",
            "model": "Claude 3 Sonnet",
            "description": "Analyzes patterns and creates strategic plans",
            "capabilities": ["Pattern Analysis", "Strategy Creation", "Risk Assessment", "Move Prediction"]
        } 