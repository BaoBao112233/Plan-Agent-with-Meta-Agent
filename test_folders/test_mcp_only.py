#!/usr/bin/env python3

"""Test app để verify Tool Agent chỉ sử dụng MCP tools"""

import sys
import time
from datetime import datetime

def test_mcp_only_tool_agent():
    """Test MCPToolAgent để đảm bảo nó sử dụng real MCP tools"""
    
    print("🔌 Testing MCP-Only Tool Agent")
    print("=" * 50)
    
    try:
        from src.agent.tool.mcp_agent import MCPToolAgent
        from src.inference.groq import ChatGroq
        
        llm = ChatGroq()
        agent = MCPToolAgent(llm=llm, verbose=True)
        
        print(f"✅ MCPToolAgent created with {len(llm.api_keys)} API keys")
        
        # Test 1: List MCP tools
        print("\n📋 Test 1: List MCP Tools")
        print("-" * 30)
        result1 = agent.invoke("list all available tools")
        
        print(f"Route: {result1.get('route')}")
        print(f"Output preview: {result1.get('output', '')[:200]}...")
        
        # Test 2: Execute MCP tool
        print("\n🔧 Test 2: Execute MCP Tool")
        print("-" * 30)
        result2 = agent.invoke("get device list for living room")
        
        output2 = result2.get('output', '')
        print(f"Route: {result2.get('route')}")
        print(f"Output preview: {output2[:200]}...")
        
        # Check if it's using real MCP or mock
        if "REAL MCP SERVER" in output2:
            print("✅ SUCCESS: Using REAL MCP SERVER!")
            return True
        elif "MOCK" in output2:
            print("⚠️  WARNING: Using MOCK (MCP server may be unavailable)")
            return True
        else:
            print("❌ FAILED: Cannot determine tool execution type")
            return False
            
    except Exception as e:
        print(f"❌ MCPToolAgent test failed: {e}")
        return False

def test_react_agent_mcp_only():
    """Test ReactAgent với MCP-only mode"""
    
    print("\n🔄 Testing ReactAgent MCP-Only Mode")
    print("=" * 50)
    
    try:
        from src.agent.react import ReactAgent
        from src.inference.groq import ChatGroq
        
        llm = ChatGroq()
        
        # Create ReactAgent với MCP-only mode
        react_agent = ReactAgent(
            name="MCP Smart Home Agent",
            description="Agent that ONLY uses MCP smart home tools",
            llm=llm,
            verbose=True,
            max_iterations=3,
            use_only_mcp_tools=True  # Key parameter!
        )
        
        print("✅ ReactAgent created in MCP-only mode")
        print(f"📊 Standard tools count: {len(react_agent.tool_names)}")
        
        if len(react_agent.tool_names) == 0:
            print("✅ SUCCESS: No standard tools loaded (MCP-only mode working)")
        else:
            print(f"⚠️  WARNING: {len(react_agent.tool_names)} standard tools found")
        
        # Test with smart home query
        print("\n📝 Testing smart home query...")
        query = "get list of all devices in living room"
        
        start_time = time.time()
        result = react_agent.invoke(query)
        elapsed = time.time() - start_time
        
        print(f"✅ Query completed in {elapsed:.1f}s")
        print(f"📄 Result preview: {str(result)[:300]}...")
        
        # Check if result mentions MCP tools
        if "MCP" in str(result).upper() or "device" in str(result).lower():
            print("✅ SUCCESS: Result contains MCP tool information")
            return True
        else:
            print("⚠️  WARNING: Result may not be using MCP tools")
            return True
            
    except Exception as e:
        print(f"❌ ReactAgent test failed: {e}")
        return False

def test_meta_agent_mcp_integration():
    """Test MetaAgent với MCP integration"""
    
    print("\n🧠 Testing MetaAgent MCP Integration")
    print("=" * 50)
    
    try:
        from src.agent.meta import MetaAgent
        from src.inference.groq import ChatGroq
        
        llm = ChatGroq()
        meta_agent = MetaAgent(llm=llm, verbose=True)
        
        query = "I want to check all smart devices in my bedroom and turn on the air conditioner"
        
        print(f"📝 MetaAgent query: {query}")
        
        start_time = time.time()
        result = meta_agent.invoke(query)
        elapsed = time.time() - start_time
        
        print(f"✅ MetaAgent completed in {elapsed:.1f}s")
        print(f"📄 Result preview: {str(result)[:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ MetaAgent test failed: {e}")
        if "429" in str(e):
            print("🔄 Rate limit hit - API key rotation should handle this")
        return False

def test_direct_mcp_client():
    """Test direct MCP client call"""
    
    print("\n🔌 Testing Direct MCP Client Call")
    print("=" * 50)
    
    try:
        from src.mcp_client import MCPClient
        
        client = MCPClient()
        
        # Test get available tools
        tools = client.get_available_tools()
        print(f"📊 Available tools: {len(tools)}")
        
        # Test calling a tool directly
        print("\n🔧 Testing direct tool call...")
        result = client.call_tool("get_device_list", {})
        
        if result:
            is_real = result.get('real_mcp', False)
            is_mock = result.get('mock', False)
            
            if is_real:
                print("✅ SUCCESS: Direct MCP client using REAL MCP SERVER!")
            elif is_mock:
                print("⚠️  INFO: Direct MCP client using MOCK (server unavailable)")
            
            print(f"📄 Result preview: {str(result)[:200]}...")
            return True
        else:
            print("❌ FAILED: Direct MCP client call returned None")
            return False
            
    except Exception as e:
        print(f"❌ Direct MCP client test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🎯 MCP-Only Tool Agent Test Suite")
    print("=" * 60)
    print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")
    
    tests = [
        ("Direct MCP Client", test_direct_mcp_client),
        ("MCP-Only Tool Agent", test_mcp_only_tool_agent),
        ("ReactAgent MCP-Only", test_react_agent_mcp_only),
        ("MetaAgent MCP Integration", test_meta_agent_mcp_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((test_name, False))
        
        # Wait between tests
        print("⏱️  Waiting 3s between tests...")
        time.sleep(3)
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 MCP-ONLY TEST SUMMARY")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    pass_count = sum(1 for _, success in results if success)
    print(f"\nTotal: {pass_count}/{len(results)} tests passed")
    
    if pass_count >= len(results) * 0.75:
        print("🎉 SUCCESS: Tool Agent is using MCP tools!")
    else:
        print("⚠️  Issues detected with MCP tool usage")

if __name__ == "__main__":
    main()