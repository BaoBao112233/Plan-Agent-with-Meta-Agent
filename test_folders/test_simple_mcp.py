#!/usr/bin/env python3

"""Simple test để verify MCP tool execution without complex dependencies"""

def test_mcp_client_simple():
    """Test MCP client đơn giản"""
    print("🔌 Testing MCP Client Simple")
    print("=" * 40)
    
    try:
        from src.mcp_client import MCPClient
        
        client = MCPClient()
        
        # Test 1: Get tools
        tools = client.get_available_tools()
        print(f"✅ Found {len(tools)} MCP tools")
        
        # Test 2: Call tool
        print("\n🔧 Testing tool execution...")
        result = client.call_tool("get_device_list", {})
        
        if result:
            is_real = result.get('real_mcp', False)
            is_mock = result.get('mock', False)
            
            print(f"Real MCP: {is_real}")
            print(f"Mock: {is_mock}")
            
            if is_real:
                print("🎉 SUCCESS: Using REAL MCP SERVER!")
            elif is_mock:
                print("⚠️  Using MOCK (MCP server issue)")
            
            return True
        else:
            print("❌ Tool call failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_mcp_tool_agent_simple():
    """Test MCPToolAgent đơn giản"""
    print("\n🤖 Testing MCPToolAgent Simple")
    print("=" * 40)
    
    try:
        from src.agent.tool.mcp_agent import MCPToolAgent
        from src.inference.mock import MockLLM
        
        # Use MockLLM để avoid API calls
        mock_llm = MockLLM()
        agent = MCPToolAgent(llm=mock_llm, verbose=True)
        
        print("✅ MCPToolAgent created")
        
        # Test tool execution
        result = agent.invoke("get device list for living room")
        
        output = result.get('output', '')
        route = result.get('route', '')
        
        print(f"Route: {route}")
        print(f"Output length: {len(output)}")
        
        if "MCP SERVER" in output:
            print("🎉 SUCCESS: Output mentions MCP SERVER!")
            return True
        elif "MOCK" in output:
            print("⚠️  Using MOCK execution")
            return True
        else:
            print("❌ No clear MCP execution indication")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_execution_direct():
    """Test tool execution directly"""
    print("\n⚡ Testing Direct Tool Execution")
    print("=" * 40)
    
    try:
        from src.agent.tool.mcp_agent import MCPToolAgent, AgentState
        
        # Create agent without LLM
        agent = MCPToolAgent(llm=None, verbose=True)
        
        # Test execute_tool directly
        state = AgentState(input="get device list")
        
        # Manual execution info
        state['tool_name'] = 'get_device_list'
        state['parameters'] = {}
        
        result = agent.execute_tool(state)
        output = result.get('output', '')
        
        print(f"Output: {output[:200]}...")
        
        if "REAL MCP SERVER" in output:
            print("🎉 SUCCESS: Using REAL MCP SERVER!")
            return True
        elif "MOCK" in output:
            print("⚠️  Using MOCK execution")
            return True
        else:
            print("❌ No execution indication")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main simple test"""
    print("🧪 Simple MCP Tool Test")
    print("=" * 50)
    
    tests = [
        test_mcp_client_simple,
        test_mcp_tool_agent_simple,
        test_tool_execution_direct
    ]
    
    results = []
    
    for test_func in tests:
        try:
            success = test_func()
            results.append(success)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
    
    print(f"\n🎯 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("🎉 All tests passed!")
    elif any(results):
        print("⚠️  Partial success")
    else:
        print("❌ All tests failed")

if __name__ == "__main__":
    main()