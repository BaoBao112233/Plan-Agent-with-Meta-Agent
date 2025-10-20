#!/usr/bin/env python3

"""Simple test để debug response issue"""

from src.agent.tool.mcp_agent import MCPToolAgent, AgentState

def test_mcp_tool_agent():
    """Test MCPToolAgent without complex workflows"""
    
    print("🧪 Testing MCPToolAgent directly")
    print("=" * 50)
    
    # Create agent without LLM to avoid API issues
    agent = MCPToolAgent(llm=None)
    
    # Test 1: List tools
    print("\n1️⃣ Testing list_tools:")
    state = AgentState(input='list all available tools')
    result = agent.list_tools(state)
    output = result.get('output', 'NO OUTPUT')
    print(f"Output length: {len(output)}")
    print(f"First 200 chars: {output[:200]}...")
    
    # Test 2: Check tools count  
    tools = agent.mcp_client.get_available_tools()
    print(f"\n2️⃣ MCP Client has {len(tools)} tools:")
    for i, (name, info) in enumerate(tools.items(), 1):
        desc = info.get('description', 'No description')
        print(f"   {i}. {name}: {desc[:50]}...")
    
    # Test 3: Simulate user query result
    print(f"\n3️⃣ Simulated user response:")
    if output and len(output) > 100:
        print("✅ Response is good - contains tool information")
        return True
    else:
        print("❌ Response is empty or too short")
        print(f"Raw output: {repr(output)}")
        return False

if __name__ == "__main__":
    success = test_mcp_tool_agent()
    print(f"\n🎯 Test Result: {'SUCCESS' if success else 'FAILED'}")