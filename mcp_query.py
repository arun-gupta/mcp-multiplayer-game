#!/usr/bin/env python3
"""
Interactive MCP Query Tool
Query MCP servers interactively
"""
import requests
import json
import sys
from typing import Dict, Any, List


class MCPQueryTool:
    def __init__(self):
        self.base_url = "http://localhost:8000/mcp"
        self.agents = ["scout", "strategist", "executor"]
    
    def query(self, agent_id: str, method: str, params: Dict[str, Any] = {}) -> Dict:
        """Query MCP server with JSON-RPC"""
        try:
            response = requests.post(
                f"{self.base_url}/{agent_id}",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": method,
                    "params": params
                },
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def list_tools(self, agent_id: str) -> List[Dict]:
        """List all tools for an agent"""
        result = self.query(agent_id, "tools/list")
        if "result" in result:
            return result["result"].get("tools", [])
        return []
    
    def list_resources(self, agent_id: str) -> List[Dict]:
        """List all resources for an agent"""
        result = self.query(agent_id, "resources/list")
        if "result" in result:
            return result["result"].get("resources", [])
        return []
    
    def list_prompts(self, agent_id: str) -> List[Dict]:
        """List all prompts for an agent"""
        result = self.query(agent_id, "prompts/list")
        if "result" in result:
            return result["result"].get("prompts", [])
        return []
    
    def call_tool(self, agent_id: str, tool_name: str, arguments: Dict[str, Any] = {}) -> Dict:
        """Call a specific tool"""
        return self.query(agent_id, "tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
    
    def read_resource(self, agent_id: str, uri: str) -> Dict:
        """Read a specific resource"""
        return self.query(agent_id, "resources/read", {"uri": uri})
    
    def get_prompt(self, agent_id: str, name: str, arguments: Dict[str, Any] = {}) -> Dict:
        """Get a specific prompt"""
        return self.query(agent_id, "prompts/get", {
            "name": name,
            "arguments": arguments
        })
    
    def show_agent_summary(self, agent_id: str):
        """Show comprehensive agent summary"""
        print(f"\n🤖 {agent_id.upper()} AGENT")
        print("=" * 50)
        
        # Tools
        tools = self.list_tools(agent_id)
        print(f"\n📋 {len(tools)} Tools:")
        for tool in tools:
            print(f"  • {tool['name']}: {tool['description']}")
        
        # Resources
        resources = self.list_resources(agent_id)
        print(f"\n📦 {len(resources)} Resources:")
        for resource in resources:
            print(f"  • {resource['name']}: {resource['description']}")
        
        # Prompts
        prompts = self.list_prompts(agent_id)
        print(f"\n💬 {len(prompts)} Prompts:")
        for prompt in prompts:
            print(f"  • {prompt['name']}: {prompt['description']}")
    
    def interactive_mode(self):
        """Interactive query mode"""
        print("🔍 MCP Interactive Query Tool")
        print("=" * 40)
        
        while True:
            print(f"\nAvailable agents: {', '.join(self.agents)}")
            print("Commands: status, tools, resources, prompts, call, read, prompt, summary, quit")
            
            try:
                cmd = input("\n> ").strip().lower()
                
                if cmd == "quit":
                    break
                elif cmd == "summary":
                    agent = input("Agent: ").strip()
                    if agent in self.agents:
                        self.show_agent_summary(agent)
                    else:
                        print("❌ Invalid agent")
                
                elif cmd == "status":
                    agent = input("Agent: ").strip()
                    if agent in self.agents:
                        result = self.call_tool(agent, "get_status")
                        if "result" in result:
                            content = json.loads(result["result"]["content"][0]["text"])
                            print(f"✅ {content.get('role')} - {content.get('current_model')}")
                            print(f"✅ Running: {content.get('is_running')}")
                            print(f"✅ Port: {content.get('mcp_port')}")
                        else:
                            print(f"❌ Error: {result.get('error')}")
                    else:
                        print("❌ Invalid agent")
                
                elif cmd == "tools":
                    agent = input("Agent: ").strip()
                    if agent in self.agents:
                        tools = self.list_tools(agent)
                        print(f"\n📋 {len(tools)} Tools:")
                        for tool in tools:
                            print(f"  • {tool['name']}: {tool['description']}")
                    else:
                        print("❌ Invalid agent")
                
                elif cmd == "resources":
                    agent = input("Agent: ").strip()
                    if agent in self.agents:
                        resources = self.list_resources(agent)
                        print(f"\n📦 {len(resources)} Resources:")
                        for resource in resources:
                            print(f"  • {resource['name']} ({resource['uri']})")
                    else:
                        print("❌ Invalid agent")
                
                elif cmd == "prompts":
                    agent = input("Agent: ").strip()
                    if agent in self.agents:
                        prompts = self.list_prompts(agent)
                        print(f"\n💬 {len(prompts)} Prompts:")
                        for prompt in prompts:
                            print(f"  • {prompt['name']}: {prompt['description']}")
                    else:
                        print("❌ Invalid agent")
                
                elif cmd == "call":
                    agent = input("Agent: ").strip()
                    tool = input("Tool name: ").strip()
                    args = input("Arguments (JSON, or empty): ").strip()
                    
                    if agent in self.agents:
                        try:
                            arguments = json.loads(args) if args else {}
                            result = self.call_tool(agent, tool, arguments)
                            print(json.dumps(result, indent=2))
                        except json.JSONDecodeError:
                            print("❌ Invalid JSON")
                    else:
                        print("❌ Invalid agent")
                
                elif cmd == "read":
                    agent = input("Agent: ").strip()
                    uri = input("Resource URI: ").strip()
                    
                    if agent in self.agents:
                        result = self.read_resource(agent, uri)
                        print(json.dumps(result, indent=2))
                    else:
                        print("❌ Invalid agent")
                
                elif cmd == "prompt":
                    agent = input("Agent: ").strip()
                    name = input("Prompt name: ").strip()
                    args = input("Arguments (JSON, or empty): ").strip()
                    
                    if agent in self.agents:
                        try:
                            arguments = json.loads(args) if args else {}
                            result = self.get_prompt(agent, name, arguments)
                            print(json.dumps(result, indent=2))
                        except json.JSONDecodeError:
                            print("❌ Invalid JSON")
                    else:
                        print("❌ Invalid agent")
                
                else:
                    print("❌ Unknown command")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Command line mode
        tool = MCPQueryTool()
        agent = sys.argv[1]
        method = sys.argv[2] if len(sys.argv) > 2 else "tools/list"
        
        if method == "tools/list":
            tools = tool.list_tools(agent)
            print(json.dumps(tools, indent=2))
        elif method == "resources/list":
            resources = tool.list_resources(agent)
            print(json.dumps(resources, indent=2))
        elif method == "prompts/list":
            prompts = tool.list_prompts(agent)
            print(json.dumps(prompts, indent=2))
        elif method == "status":
            result = tool.call_tool(agent, "get_status")
            print(json.dumps(result, indent=2))
        else:
            print("Usage: python mcp_query.py <agent> [method]")
            print("Methods: tools/list, resources/list, prompts/list, status")
    else:
        # Interactive mode
        tool = MCPQueryTool()
        tool.interactive_mode()


if __name__ == "__main__":
    main()
