#!/usr/bin/env python3
"""
Test script để kiểm tra MCP Tool Agent integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.tool import ToolAgent  # This now imports MCPToolAgent
from src.inference.groq import ChatGroq
from src.mcp_client import MCPClient
from dotenv import load_dotenv
from os import environ

load_dotenv()

def test_mcp_client():
    """Test MCPClient độc lập"""
    print("🧪 Testing MCP Client...")
    
    mcp_client = MCPClient()
    
    # Test get available tools
    print("\n1. Testing get_available_tools...")
    tools = mcp_client.get_available_tools()
    if tools:
        print(f"✅ Found {len(tools)} tools:")
        for tool_name in tools.keys():
            print(f"  - {tool_name}")
    else:
        print("❌ No tools found or connection failed")
        return False
    
    # Test get tool info
    if tools:
        first_tool = list(tools.keys())[0]
        print(f"\n2. Testing get_tool_info for '{first_tool}'...")
        tool_info = mcp_client.get_tool_info(first_tool)
        if tool_info:
            print(f"✅ Tool info retrieved:")
            print(f"  Description: {tool_info.get('description', 'N/A')}")
            print(f"  Parameters: {list(tool_info.get('parameters', {}).keys())}")
        else:
            print("❌ Failed to get tool info")
    
    # Test search tools
    print("\n3. Testing search_tools...")
    search_results = mcp_client.search_tools("device")
    if search_results:
        print(f"✅ Found {len(search_results)} tools matching 'device':")
        for result in search_results[:3]:  # Show first 3
            print(f"  - {result['name']} (matched by {result['match_reason']})")
    else:
        print("❌ No search results found")
    
    return True

def test_mcp_tool_agent():
    """Test MCP Tool Agent"""
    print("\n🤖 Testing MCP Tool Agent...")
    
    api_key = environ.get("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found. Please set it in .env file.")
        return False
    
    try:
        llm = ChatGroq('llama-3.3-70b-versatile', api_key, temperature=0)
        
        # Initialize MCP Tool Agent
        tool_agent = ToolAgent(llm=llm, verbose=True)
        
        print("\n--- Test 1: List all tools ---")
        response = tool_agent.invoke("list all available tools")
        print(f"Response: {response['output'][:200]}...")
        
        print("\n--- Test 2: Search for device tools ---")
        response = tool_agent.invoke("search for device control tools")
        print(f"Response: {response['output'][:200]}...")
        
        print("\n--- Test 3: Get info about a specific tool ---")
        response = tool_agent.invoke("get info about get_device_list")
        print(f"Response: {response['output'][:200]}...")
        
        print("\n--- Test 4: Help with tool usage ---")
        response = tool_agent.invoke("help me with using tools")
        print(f"Response: {response['output'][:200]}...")
        
        print("\n✅ MCP Tool Agent tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing MCP Tool Agent: {e}")
        return False

def test_tool_execution():
    """Test actual tool execution (if MCP server supports it)"""
    print("\n🔧 Testing Tool Execution...")
    
    api_key = environ.get("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found.")
        return False
    
    try:
        llm = ChatGroq('llama-3.3-70b-versatile', api_key, temperature=0)
        tool_agent = ToolAgent(llm=llm, verbose=True)
        
        # This would require a valid token and proper MCP server setup
        print("\n--- Test: Execute get_device_list (might fail without valid token) ---")
        response = tool_agent.invoke("execute get_device_list with token=test_token")
        print(f"Response: {response['output'][:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing tool execution: {e}")
        return False

def main():
    print("🚀 Starting MCP Tool Agent Integration Tests\n")
    
    # Check if MCP server is running
    try:
        import requests
        response = requests.get("http://localhost:9031/sse", timeout=5)
        if response.status_code == 200:
            print("✅ MCP Server is running at http://localhost:9031")
        else:
            print("⚠️  MCP Server might not be running properly")
    except Exception as e:
        print(f"❌ Cannot connect to MCP Server at http://localhost:9031: {e}")
        print("Please make sure the MCP server is running before testing.")
        print("You can start it with: cd /path/to/mcp/oxii-server && docker compose up -d")
        return
    
    print("\n" + "="*60)
    
    # Test MCP Client
    if test_mcp_client():
        print("\n" + "="*60)
        
        # Test MCP Tool Agent
        if test_mcp_tool_agent():
            print("\n" + "="*60)
            
            # Test tool execution (optional)
            test_tool_execution()
    else:
        print("❌ MCP Client tests failed. Skipping other tests.")

if __name__ == "__main__":
    main()