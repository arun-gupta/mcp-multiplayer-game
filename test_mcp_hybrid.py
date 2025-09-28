"""
Test script for MCP Hybrid Architecture
Tests the new CrewAI + MCP hybrid agents
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.scout import ScoutMCPAgent
from agents.strategist import StrategistMCPAgent
from agents.executor import ExecutorMCPAgent
from game.mcp_coordinator import MCPGameCoordinator


async def test_mcp_agents():
    """Test the MCP hybrid agents"""
    print("🧪 Testing MCP Hybrid Architecture...")
    
    try:
        # Test Scout Agent
        print("\n1. Testing Scout MCP Agent...")
        scout = ScoutMCPAgent({"model": "gpt-4"})
        await scout.start_mcp_server()
        
        # Test board analysis
        board_data = {
            "board": [["X", "", ""], ["", "O", ""], ["", "", ""]],
            "current_player": "ai",
            "move_number": 2
        }
        
        analysis = await scout.analyze_board(board_data)
        print(f"✅ Scout analysis: {analysis.get('agent_id', 'unknown')}")
        
        # Test Strategist Agent
        print("\n2. Testing Strategist MCP Agent...")
        strategist = StrategistMCPAgent({"model": "gpt-4"})
        await strategist.start_mcp_server()
        
        # Test strategy creation
        strategy = await strategist.create_strategy(analysis)
        print(f"✅ Strategist strategy: {strategy.get('agent_id', 'unknown')}")
        
        # Test Executor Agent
        print("\n3. Testing Executor MCP Agent...")
        executor = ExecutorMCPAgent({"model": "gpt-4"})
        await executor.start_mcp_server()
        
        # Test move execution
        execution = await executor.execute_move(strategy)
        print(f"✅ Executor execution: {execution.get('agent_id', 'unknown')}")
        
        # Test MCP Coordinator
        print("\n4. Testing MCP Coordinator...")
        coordinator = MCPGameCoordinator()
        await coordinator.initialize_agents()
        
        # Test agent status
        status = coordinator.get_agent_status()
        print(f"✅ Coordinator status: {status.get('coordinator_status', 'unknown')}")
        
        print("\n🎉 All MCP Hybrid tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_communication():
    """Test agent-to-agent communication via MCP"""
    print("\n🔗 Testing Agent Communication...")
    
    try:
        # Initialize all agents
        scout = ScoutMCPAgent({"model": "gpt-4"})
        strategist = StrategistMCPAgent({"model": "gpt-4"})
        executor = ExecutorMCPAgent({"model": "gpt-4"})
        
        # Start MCP servers
        await scout.start_mcp_server()
        await strategist.start_mcp_server()
        await executor.start_mcp_server()
        
        # Test the full workflow
        print("Testing Scout -> Strategist -> Executor workflow...")
        
        # Scout analyzes board
        board_data = {
            "board": [["X", "", ""], ["", "O", ""], ["", "", ""]],
            "current_player": "ai",
            "move_number": 2
        }
        
        observation = await scout.analyze_board(board_data)
        print(f"Scout observation: {observation.get('agent_id')}")
        
        # Strategist creates strategy
        strategy = await strategist.create_strategy(observation)
        print(f"Strategist strategy: {strategy.get('agent_id')}")
        
        # Executor executes move
        execution = await executor.execute_move(strategy)
        print(f"Executor execution: {execution.get('agent_id')}")
        
        print("✅ Agent communication workflow completed!")
        return True
        
    except Exception as e:
        print(f"❌ Communication test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 Starting MCP Hybrid Architecture Tests")
    print("=" * 50)
    
    # Test individual agents
    agents_ok = await test_mcp_agents()
    
    # Test agent communication
    communication_ok = await test_agent_communication()
    
    print("\n" + "=" * 50)
    if agents_ok and communication_ok:
        print("🎉 All tests passed! MCP Hybrid Architecture is working.")
        print("\nNext steps:")
        print("1. Run: python main_mcp.py")
        print("2. Test the API endpoints")
        print("3. Integrate with MCP Inspector")
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
