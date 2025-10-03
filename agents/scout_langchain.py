"""
LangChain-based Scout Agent for Tic-Tac-Toe
Replaces CrewAI Scout with direct LangChain implementation
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


class BoardAnalysis(BaseModel):
    """Structured output for board analysis"""
    threats: List[Dict[str, int]] = Field(description="List of immediate threats (opponent can win)")
    opportunities: List[Dict[str, int]] = Field(description="List of winning opportunities (we can win)")
    strategic_moves: List[Dict[str, int]] = Field(description="List of strategic moves (center, corners, etc.)")
    analysis: str = Field(description="Detailed analysis of the board state")


class ScoutLangChain:
    """LangChain-based Scout agent for board analysis"""
    
    def __init__(self, model_name: str = "gpt-5-mini"):
        self.model_name = model_name
        self.llm = self._create_llm()
        self.parser = PydanticOutputParser(pydantic_object=BoardAnalysis)
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Tic-Tac-Toe board analysis expert. Your job is to analyze the current board state and identify:
1. IMMEDIATE THREATS: Positions where the opponent can win in their next move
2. WINNING OPPORTUNITIES: Positions where we can win in our next move  
3. STRATEGIC MOVES: Best positions for center control, corner control, etc.

Analyze the board and provide structured output with threats, opportunities, and strategic moves.
{format_instructions}"""),
            ("human", """Analyze this Tic-Tac-Toe board:
Board: {board}
Current Player: {current_player}
Available Moves: {available_moves}

Provide your analysis:""")
        ])
    
    def _create_llm(self):
        """Create the appropriate LLM based on model name"""
        if "gpt" in self.model_name.lower():
            # GPT-5 models don't support custom temperature, use default
            return ChatOpenAI(
                model=self.model_name,
                timeout=10.0
            )
        elif "claude" in self.model_name.lower():
            return ChatAnthropic(
                model=self.model_name,
                temperature=0.1,
                timeout=10.0
            )
        else:
            # Use LiteLLM for other models
            return ChatLiteLLM(
                model=self.model_name,
                temperature=0.1,
                timeout=10.0
            )
    
    async def analyze_board(self, board_state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the board and return structured analysis"""
        try:
            print(f"[DEBUG] ScoutLangChain: Starting board analysis")
            
            # Prepare the input
            board = board_state.get("board", [])
            current_player = board_state.get("current_player", "O")
            available_moves = board_state.get("available_moves", [])
            
            # Create the chain
            chain = self.prompt | self.llm | self.parser
            
            # Make the call
            result = await chain.ainvoke({
                "board": json.dumps(board),
                "current_player": current_player,
                "available_moves": json.dumps(available_moves),
                "format_instructions": self.parser.get_format_instructions()
            })
            
            print(f"[DEBUG] ScoutLangChain: Analysis completed successfully")
            
            return {
                "success": True,
                "threats": result.threats,
                "opportunities": result.opportunities,
                "strategic_moves": result.strategic_moves,
                "analysis": result.analysis,
                "available_moves": available_moves
            }
            
        except Exception as e:
            print(f"[DEBUG] ScoutLangChain: Analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "threats": [],
                "opportunities": [],
                "strategic_moves": [],
                "analysis": "Analysis failed",
                "available_moves": board_state.get("available_moves", [])
            }
    
    async def detect_threats(self, board_state: Dict[str, Any]) -> List[Dict[str, int]]:
        """Detect immediate threats on the board"""
        analysis = await self.analyze_board(board_state)
        return analysis.get("threats", [])
    
    async def identify_opportunities(self, board_state: Dict[str, Any]) -> List[Dict[str, int]]:
        """Identify winning opportunities"""
        analysis = await self.analyze_board(board_state)
        return analysis.get("opportunities", [])
    
    async def get_strategic_moves(self, board_state: Dict[str, Any]) -> List[Dict[str, int]]:
        """Get strategic move recommendations"""
        analysis = await self.analyze_board(board_state)
        return analysis.get("strategic_moves", [])
