#!/usr/bin/env python
"""
Test MCP Tools - Interactive tool discovery and testing
"""
import requests
import json
from typing import Dict, Any


def list_tools(agent_id: str) -> Dict:
    """List all tools for an agent"""
    response = requests.get(f"http://localhost:8000/mcp/{agent_id}")
    return response.json()


def list_resources(agent_id: str) -> Dict:
    """List all resources for an agent"""
    response = requests.post(
        f"http://localhost:8000/mcp/{agent_id}",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/list",
            "params": {}
        }
    )
    return response.json()


def list_prompts(agent_id: str) -> Dict:
    """List all prompts for an agent"""
    response = requests.post(
        f"http://localhost:8000/mcp/{agent_id}",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "prompts/list",
            "params": {}
        }
    )
    return response.json()


def call_tool(agent_id: str, tool_name: str, arguments: Dict[str, Any] = {}) -> Dict:
    """Call a specific tool"""
    response = requests.post(
        f"http://localhost:8000/mcp/{agent_id}",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
    )
    return response.json()


def main():
    """Test all MCP agents"""
    agents = ["scout", "strategist", "executor"]
    
    print("="*60)
    print("🔍 MCP TOOL DISCOVERY")
    print("="*60)
    
    for agent_id in agents:
        print(f"\n{'='*60}")
        print(f"🤖 {agent_id.upper()} AGENT")
        print(f"{'='*60}")
        
        # List tools
        try:
            tools_response = list_tools(agent_id)
            tools = tools_response.get('result', {}).get('tools', [])
            
            print(f"\n📋 {len(tools)} Tools Available:")
            for i, tool in enumerate(tools, 1):
                print(f"\n{i}. {tool['name']}")
                print(f"   Description: {tool['description']}")
                if tool.get('inputSchema', {}).get('required'):
                    print(f"   Required: {tool['inputSchema']['required']}")
            
            # List resources
            resources_response = list_resources(agent_id)
            resources = resources_response.get('result', {}).get('resources', [])
            print(f"\n📦 {len(resources)} Resources Available:")
            for i, resource in enumerate(resources, 1):
                print(f"\n{i}. {resource['name']}")
                print(f"   URI: {resource['uri']}")
                print(f"   Description: {resource['description']}")
                print(f"   MIME Type: {resource['mimeType']}")
            
            # List prompts
            prompts_response = list_prompts(agent_id)
            prompts = prompts_response.get('result', {}).get('prompts', [])
            print(f"\n💬 {len(prompts)} Prompts Available:")
            for i, prompt in enumerate(prompts, 1):
                print(f"\n{i}. {prompt['name']}")
                print(f"   Description: {prompt['description']}")
                if prompt.get('arguments'):
                    print(f"   Arguments: {[arg['name'] for arg in prompt['arguments']]}")
            
            # Test get_status tool
            print(f"\n🧪 Testing 'get_status' tool...")
            result = call_tool(agent_id, "get_status")
            
            if 'result' in result:
                content = json.loads(result['result']['content'][0]['text'])
                print(f"   ✅ Status: {content.get('role')} - {content.get('current_model')}")
                print(f"   ✅ Running: {content.get('is_running')}")
                print(f"   ✅ Port: {content.get('mcp_port')}")
            else:
                print(f"   ❌ Error: {result.get('error')}")
            
            # Test get_metrics tool
            print(f"\n📊 Testing 'get_metrics' tool...")
            result = call_tool(agent_id, "get_metrics")
            
            if 'result' in result:
                content = json.loads(result['result']['content'][0]['text'])
                print(f"   ✅ Requests: {content.get('request_count')}")
                print(f"   ✅ Avg Time: {content.get('avg_response_time')}s")
                print(f"   ✅ Total Tokens: {content.get('total_tokens')}")
            else:
                print(f"   ❌ Error: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error querying {agent_id}: {e}")
    
    print(f"\n{'='*60}")
    print("✅ MCP Tool Discovery Complete!")
    print("="*60)
    print("\n💡 To test specific tools with custom inputs:")
    print("   Edit this script and add your own tool calls")
    print("\n🔍 To use MCP Inspector:")
    print("   npx @modelcontextprotocol/inspector")
    print("   Connect to: http://localhost:8000/mcp/scout")
    print("="*60)


if __name__ == "__main__":
    main()

