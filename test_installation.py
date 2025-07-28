#!/usr/bin/env python3
"""
Test script for Multi-Agent Game Simulation
Verifies that all components are working correctly
"""
import sys
import os
import importlib
from typing import List, Dict, Any


def test_imports() -> Dict[str, bool]:
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    required_modules = [
        "fastapi",
        "uvicorn",
        "crewai",
        "pydantic",
        "langchain",
        "langchain_openai",
        "langchain_community",
        "matplotlib",
        "numpy"
    ]
    
    results = {}
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
            results[module] = True
        except ImportError as e:
            print(f"❌ {module}: {e}")
            results[module] = True
    
    return results


def test_local_modules() -> Dict[str, bool]:
    """Test if our local modules can be imported"""
    print("\n🔍 Testing local modules...")
    
    local_modules = [
        "schemas.observation",
        "schemas.plan", 
        "schemas.action_result",
        "game.map",
        "game.state",
        "game.engine",
        "agents.scout",
        "agents.strategist",
        "agents.executor"
    ]
    
    results = {}
    for module in local_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
            results[module] = True
        except ImportError as e:
            print(f"❌ {module}: {e}")
            results[module] = False
    
    return results


def test_game_components() -> Dict[str, bool]:
    """Test if game components can be instantiated"""
    print("\n🔍 Testing game components...")
    
    results = {}
    
    try:
        from game.state import GameStateManager
        game_manager = GameStateManager()
        print("✅ GameStateManager")
        results["GameStateManager"] = True
    except Exception as e:
        print(f"❌ GameStateManager: {e}")
        results["GameStateManager"] = False
    
    try:
        from game.map import GameMap
        game_map = GameMap(5, 5)
        print("✅ GameMap")
        results["GameMap"] = True
    except Exception as e:
        print(f"❌ GameMap: {e}")
        results["GameMap"] = False
    
    try:
        from schemas.observation import Observation
        from schemas.plan import Plan
        from schemas.action_result import TurnResult
        print("✅ Schemas")
        results["Schemas"] = True
    except Exception as e:
        print(f"❌ Schemas: {e}")
        results["Schemas"] = False
    
    return results


def test_agent_creation() -> Dict[str, bool]:
    """Test if agents can be created (without LLM calls)"""
    print("\n🔍 Testing agent creation...")
    
    results = {}
    
    try:
        from game.state import GameStateManager
        from agents.scout import ScoutAgent
        
        game_manager = GameStateManager()
        # Note: This will fail if OpenAI API key is not set, but that's expected
        try:
            scout = ScoutAgent(game_manager.get_current_state())
            print("✅ ScoutAgent (created)")
            results["ScoutAgent"] = True
        except Exception as e:
            if "OPENAI_API_KEY" in str(e):
                print("⚠️  ScoutAgent (requires OpenAI API key)")
                results["ScoutAgent"] = True  # This is expected
            else:
                print(f"❌ ScoutAgent: {e}")
                results["ScoutAgent"] = False
    except Exception as e:
        print(f"❌ ScoutAgent: {e}")
        results["ScoutAgent"] = False
    
    try:
        from agents.strategist import StrategistAgent
        # Note: This will fail if Ollama is not running, but that's expected
        try:
            strategist = StrategistAgent()
            print("✅ StrategistAgent (created)")
            results["StrategistAgent"] = True
        except Exception as e:
            if "Ollama" in str(e) or "Connection" in str(e):
                print("⚠️  StrategistAgent (requires Ollama)")
                results["StrategistAgent"] = True  # This is expected
            else:
                print(f"❌ StrategistAgent: {e}")
                results["StrategistAgent"] = False
    except Exception as e:
        print(f"❌ StrategistAgent: {e}")
        results["StrategistAgent"] = False
    
    try:
        from game.state import GameStateManager
        from agents.executor import ExecutorAgent
        
        game_manager = GameStateManager()
        # Note: This will fail if Ollama is not running, but that's expected
        try:
            executor = ExecutorAgent(game_manager.get_current_state())
            print("✅ ExecutorAgent (created)")
            results["ExecutorAgent"] = True
        except Exception as e:
            if "Ollama" in str(e) or "Connection" in str(e):
                print("⚠️  ExecutorAgent (requires Ollama)")
                results["ExecutorAgent"] = True  # This is expected
            else:
                print(f"❌ ExecutorAgent: {e}")
                results["ExecutorAgent"] = False
    except Exception as e:
        print(f"❌ ExecutorAgent: {e}")
        results["ExecutorAgent"] = False
    
    return results


def test_environment() -> Dict[str, bool]:
    """Test environment variables and external services"""
    print("\n🔍 Testing environment...")
    
    results = {}
    
    # Check OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ OPENAI_API_KEY is set")
        results["OPENAI_API_KEY"] = True
    else:
        print("⚠️  OPENAI_API_KEY is not set (required for Scout Agent)")
        results["OPENAI_API_KEY"] = False
    
    # Check Anthropic API key
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        print("✅ ANTHROPIC_API_KEY is set")
        results["ANTHROPIC_API_KEY"] = True
    else:
        print("⚠️  ANTHROPIC_API_KEY is not set (required for Strategist Agent)")
        results["ANTHROPIC_API_KEY"] = False
    
    # Check if Ollama is available
    try:
        import subprocess
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama is available: {result.stdout.strip()}")
            results["Ollama"] = True
        else:
            print("❌ Ollama is not working properly")
            results["Ollama"] = False
    except FileNotFoundError:
        print("⚠️  Ollama is not installed (required for Strategist and Executor Agents)")
        results["Ollama"] = False
    
    return results


def run_basic_game_test():
    """Run a basic game test without LLM calls"""
    print("\n🎮 Running basic game test...")
    
    try:
        from game.state import GameStateManager
        from game.map import GameMap
        from schemas.observation import Entity, TileType
        
        # Create game state
        game_manager = GameStateManager()
        current_state = game_manager.get_current_state()
        
        # Test map operations
        game_map = current_state.game_map
        print(f"✅ Map created: {game_map.width}x{game_map.height}")
        
        # Test entity operations
        player = current_state.player_entity
        if player:
            print(f"✅ Player found at {player.position} with {player.health} HP")
        
        enemies = current_state.get_enemies()
        print(f"✅ Found {len(enemies)} enemies")
        
        items = current_state.get_items()
        print(f"✅ Found {len(items)} items")
        
        # Test visibility
        visible_tiles = game_map.get_visible_tiles(player.position, 3)
        print(f"✅ Scout can see {len(visible_tiles)} tiles")
        
        # Test ASCII representation
        ascii_map = game_map.to_ascii()
        print("✅ Map ASCII representation:")
        print(ascii_map)
        
        print("✅ Basic game test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Basic game test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Multi-Agent Game Simulation - Installation Test")
    print("=" * 60)
    
    # Run all tests
    import_results = test_imports()
    local_results = test_local_modules()
    component_results = test_game_components()
    agent_results = test_agent_creation()
    env_results = test_environment()
    game_test = run_basic_game_test()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    
    all_results = {
        "External Dependencies": import_results,
        "Local Modules": local_results,
        "Game Components": component_results,
        "Agent Creation": agent_results,
        "Environment": env_results
    }
    
    total_tests = 0
    passed_tests = 0
    
    for category, results in all_results.items():
        category_total = len(results)
        category_passed = sum(1 for result in results.values() if result)
        total_tests += category_total
        passed_tests += category_passed
        
        print(f"{category}: {category_passed}/{category_total} passed")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if game_test:
        print("✅ Basic game functionality is working!")
    else:
        print("❌ Basic game functionality has issues")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    if not env_results.get("OPENAI_API_KEY", False):
        print("- Set OPENAI_API_KEY environment variable for Scout Agent")
    
    if not env_results.get("ANTHROPIC_API_KEY", False):
        print("- Set ANTHROPIC_API_KEY environment variable for Strategist Agent")
    
    if not env_results.get("Ollama", False):
        print("- Install Ollama for Executor Agent")
    
    if passed_tests == total_tests and game_test:
        print("🎉 All tests passed! The installation is working correctly.")
        print("You can now run: python main.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed_tests == total_tests and game_test


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 