#!/usr/bin/env python3
"""
Test script to demonstrate agent timing logs
"""

import requests
import time
import json

def test_agent_timing():
    """Test agent timing by making moves and triggering AI responses"""
    
    base_url = "http://localhost:8000"
    
    print("🎯 Testing Agent Timing Logs")
    print("=" * 50)
    
    # Reset the game
    print("🔄 Resetting game...")
    response = requests.post(f"{base_url}/reset-game")
    if response.status_code == 200:
        print("✅ Game reset successfully")
    else:
        print("❌ Failed to reset game")
        return
    
    # Make a player move
    print("\n👤 Making player move (0,0)...")
    start_time = time.time()
    response = requests.post(f"{base_url}/make-move", 
                           json={"row": 0, "col": 0})
    player_duration = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Player move completed in {player_duration:.3f}s")
        print(f"   Board: {result.get('board')}")
    else:
        print("❌ Player move failed")
        return
    
    # Trigger AI move and measure timing
    print("\n🤖 Triggering AI move...")
    print("   (Watch server console for timing logs)")
    start_time = time.time()
    response = requests.post(f"{base_url}/ai-move")
    ai_duration = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ AI move completed in {ai_duration:.3f}s")
        print(f"   Move: {result.get('move')}")
        print(f"   Reasoning: {result.get('reasoning')}")
    else:
        print("❌ AI move failed")
        return
    
    # Make another player move
    print("\n👤 Making player move (0,1)...")
    start_time = time.time()
    response = requests.post(f"{base_url}/make-move", 
                           json={"row": 0, "col": 1})
    player_duration = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Player move completed in {player_duration:.3f}s")
        print(f"   Board: {result.get('board')}")
    else:
        print("❌ Player move failed")
        return
    
    # Trigger another AI move
    print("\n🤖 Triggering AI move...")
    print("   (Watch server console for timing logs)")
    start_time = time.time()
    response = requests.post(f"{base_url}/ai-move")
    ai_duration = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ AI move completed in {ai_duration:.3f}s")
        print(f"   Move: {result.get('move')}")
        print(f"   Reasoning: {result.get('reasoning')}")
    else:
        print("❌ AI move failed")
        return
    
    # Get final game state
    print("\n📊 Final game state:")
    response = requests.get(f"{base_url}/state")
    if response.status_code == 200:
        state = response.json()
        print(f"   Board: {state.get('board')}")
        print(f"   Current player: {state.get('current_player')}")
        print(f"   Move number: {state.get('move_number')}")
        print(f"   Game over: {state.get('game_over')}")
    
    print("\n🎯 Timing Test Complete!")
    print("   Check the server console for detailed timing logs:")
    print("   - [TIMING] Scout Agent - LLM call: X.XXXs, Total: X.XXXs")
    print("   - [TIMING] Strategist Agent - LLM call: X.XXXs, Total: X.XXXs") 
    print("   - [TIMING] Executor Agent - LLM call: X.XXXs, Total: X.XXXs")
    print("   - [TIMING] Local Coordination - Total: X.XXXs")

if __name__ == "__main__":
    test_agent_timing()
