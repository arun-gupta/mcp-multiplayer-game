"""
LangChain-based Strategist Agent for Tic-Tac-Toe
Replaces CrewAI Strategist with direct LangChain implementation
"""

import json
import asyncio
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatLiteLLM
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class StrategyRecommendation(BaseModel):
    """Structured output for strategy recommendation"""
    move: Dict[str, int] = Field(description="Recommended move with row and col")
    strategy: str = Field(description="Strategy explanation")
    priority: str = Field(description="Priority level: BLOCK, WIN, STRATEGIC")
    reasoning: str = Field(description="Detailed reasoning for the move")


class StrategistLangChain:
    """LangChain-based Strategist agent for move strategy"""
    
    def __init__(self, model_name: str = "gpt-5-mini"):
        self.model_name = model_name
        self.llm = self._create_llm()
        self.parser = PydanticOutputParser(pydantic_object=StrategyRecommendation)
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Tic-Tac-Toe strategy expert. Your job is to create the optimal strategy based on board analysis.

PRIORITY ORDER:
1. BLOCK: If opponent can win next move, block them
2. WIN: If we can win next move, take the winning move
3. STRATEGIC: Choose the best strategic position (center, corners, etc.)

Analyze the threats, opportunities, and available moves to recommend the best move.
{format_instructions}"""),
            ("human", """Create strategy for this Tic-Tac-Toe situation:
Board: {board}
Threats: {threats}
Opportunities: {opportunities}
Available Moves: {available_moves}
Current Player: {current_player}

Recommend the best move:""")
        ])
    
    def _create_llm(self):
        """Create the appropriate LLM based on model name"""
        if "gpt" in self.model_name.lower():
            # GPT-5 models don't support custom temperature, use default
            return ChatOpenAI(
                model=self.model_name,
                timeout=30.0
            )
        elif "claude" in self.model_name.lower():
            return ChatAnthropic(
                model=self.model_name,
                temperature=0.1,
                timeout=30.0
            )
        else:
            # Use LiteLLM for other models
            return ChatLiteLLM(
                model=self.model_name,
                temperature=0.1,
                timeout=30.0
            )
    
    async def create_strategy(self, strategy_input: Dict[str, Any]) -> Dict[str, Any]:
        """Create strategy based on board analysis"""
        import time
        start_time = time.time()
        
        try:
            print(f"[DEBUG] StrategistLangChain: Starting strategy creation")
            
            # Prepare the input
            board = strategy_input.get("board_state", [])
            threats = strategy_input.get("threats", [])
            opportunities = strategy_input.get("opportunities", [])
            available_moves = strategy_input.get("available_moves", [])
            current_player = "O"  # AI player
            
            # Create the chain
            chain = self.prompt | self.llm | self.parser
            
            # Make the call
            llm_start = time.time()
            result = await chain.ainvoke({
                "board": json.dumps(board),
                "threats": json.dumps(threats),
                "opportunities": json.dumps(opportunities),
                "available_moves": json.dumps(available_moves),
                "current_player": current_player,
                "format_instructions": self.parser.get_format_instructions()
            })
            llm_duration = time.time() - llm_start
            
            total_duration = time.time() - start_time
            overhead = total_duration - llm_duration
            print(f"[DEBUG] StrategistLangChain: Strategy created successfully")
            print(f"[TIMING] Strategist Agent - LLM: {llm_duration:.3f}s, Overhead: {overhead:.3f}s, Total: {total_duration:.3f}s")
            
            return {
                "success": True,
                "move": result.move,
                "strategy": result.strategy,
                "priority": result.priority,
                "reasoning": result.reasoning
            }
            
        except Exception as e:
            total_duration = time.time() - start_time
            print(f"[DEBUG] StrategistLangChain: Strategy creation failed: {e}")
            print(f"[TIMING] Strategist Agent - FAILED after {total_duration:.3f}s")
            return {
                "success": False,
                "error": str(e),
                "move": {"row": 1, "col": 1},  # Fallback to center
                "strategy": "Fallback strategy",
                "priority": "STRATEGIC",
                "reasoning": "Strategy creation failed, using fallback"
            }
    
    async def evaluate_position(self, board_state: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the current board position"""
        strategy = await self.create_strategy(board_state)
        return {
            "evaluation": strategy.get("reasoning", "No evaluation available"),
            "score": 0.5,  # Neutral score
            "recommendation": strategy.get("strategy", "No recommendation")
        }
    
    async def recommend_move(self, board_state: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend the best move"""
        return await self.create_strategy(board_state)
    
    async def assess_win_probability(self, board_state: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the probability of winning"""
        strategy = await self.create_strategy(board_state)
        return {
            "win_probability": 0.5,  # Neutral probability
            "analysis": strategy.get("reasoning", "No analysis available")
        }
