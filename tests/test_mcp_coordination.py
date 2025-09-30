#!/usr/bin/env python3
"""
Test MCP coordination to see why it's failing
"""
import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.scout import ScoutMCPAgent
from agents.strategist import StrategistMCPAgent  
from agents.executor import ExecutorMCPAgent
from game.mcp_coordinator import MCPGameCoordinator
from game.state import TicTacToeGameState

async def test_mcp_coordination():
    print("🧪 Testing MCP coordination...")
    
    # Create agents
    print("Creating agents...")
    scout_agent = ScoutMCPAgent({"model": "gpt-5-mini"})
    strategist_agent = StrategistMCPAgent({"model": "gpt-5-mini"})
    executor_agent = ExecutorMCPAgent({"model": "gpt-5-mini"})
    print("✅ Agents created")
    
    # Start MCP servers
    print("Starting MCP servers...")
    await scout_agent.start_mcp_server()
    await strategist_agent.start_mcp_server()
    await executor_agent.start_mcp_server()
    print("✅ MCP servers started")
    
    # Create coordinator
    print("Creating coordinator...")
    coordinator = MCPGameCoordinator()
    coordinator.set_agents(scout_agent, strategist_agent, executor_agent)
    print(f"✅ Coordinator created with agents: {list(coordinator.agents.keys())}")
    
    # Test a simple move
    print("Testing MCP coordination...")
    try:
        result = await coordinator.process_player_move(0, 0)
        print(f"✅ MCP coordination result: {result}")
        
        # Check MCP logs
        logs = coordinator.get_mcp_logs()
        print(f"📊 MCP logs count: {len(logs)}")
        for log in logs[-3:]:  # Show last 3 logs
            print(f"  - {log.get('agent', 'unknown')}: {log.get('message_type', 'unknown')}")
            
    except Exception as e:
        print(f"❌ MCP coordination failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_mcp_coordination())
