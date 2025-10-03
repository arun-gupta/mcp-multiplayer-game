#!/usr/bin/env python3
"""
Test script to measure CrewAI performance optimizations
"""

import requests
import time
import json

def test_crewai_performance():
    """Test CrewAI performance with optimizations"""
    
    base_url = "http://localhost:8000"
    
    print("🚀 Testing CrewAI Performance Optimizations")
    print("=" * 60)
    
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
    print("\n🤖 Triggering AI move with CrewAI optimizations...")
    print("   Optimizations applied:")
    print("   • memory=False (no context retention)")
    print("   • verbose=False (reduced output processing)")
    print("   • allow_delegation=False (skip delegation logic)")
    print("   • max_iter=1 (limit reasoning loops)")
    print("   (Watch server console for timing logs)")
    
    start_time = time.time()
    response = requests.post(f"{base_url}/ai-move")
    ai_duration = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ AI move completed in {ai_duration:.3f}s")
        print(f"   Move: {result.get('move')}")
        print(f"   Reasoning: {result.get('reasoning')}")
        
        # Performance analysis
        print(f"\n📊 Performance Analysis:")
        print(f"   • Player move: {player_duration:.3f}s")
        print(f"   • AI move: {ai_duration:.3f}s")
        print(f"   • Total game time: {player_duration + ai_duration:.3f}s")
        
        if ai_duration < 30:
            print(f"   🎯 Excellent performance! AI move under 30s")
        elif ai_duration < 60:
            print(f"   ✅ Good performance! AI move under 60s")
        else:
            print(f"   ⚠️  Slow performance! AI move over 60s")
            
    else:
        print("❌ AI move failed")
        return
    
    # Make another player move to test consistency
    print("\n👤 Making player move (2,2)...")
    start_time = time.time()
    response = requests.post(f"{base_url}/make-move", 
                           json={"row": 2, "col": 2})
    player_duration = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Player move completed in {player_duration:.3f}s")
        print(f"   Board: {result.get('board')}")
    else:
        print("❌ Player move failed")
        return
    
    # Trigger another AI move
    print("\n🤖 Triggering AI move (consistency test)...")
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
    
    print("\n🎯 CrewAI Performance Test Complete!")
    print("   Check the server console for detailed timing logs:")
    print("   - [TIMING] Scout Agent - LLM: X.XXXs, Overhead: X.XXXs, Total: X.XXXs")
    print("   - [TIMING] Strategist Agent - LLM: X.XXXs, Overhead: X.XXXs, Total: X.XXXs") 
    print("   - [TIMING] Executor Agent - LLM: X.XXXs, Overhead: X.XXXs, Total: X.XXXs")
    print("   - [TIMING] Local Coordination - Total: X.XXXs")
    print("\n💡 Optimizations should show:")
    print("   • Lower overhead times (memory=False, verbose=False)")
    print("   • Faster total execution (allow_delegation=False, max_iter=1)")
    print("   • More consistent performance across moves")

if __name__ == "__main__":
    test_crewai_performance()
