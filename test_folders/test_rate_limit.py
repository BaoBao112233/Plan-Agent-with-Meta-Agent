#!/usr/bin/env python3

"""Test app với multiple LLM fallbacks để tránh rate limit"""

import sys
import time
from src.agent.tool.mcp_agent import MCPToolAgent, AgentState

def get_available_llm():
    """Get available LLM with fallback options"""
    
    print("🔍 Checking available LLM options...")
    
    # Option 1: Try Groq (with rate limiting)
    try:
        from src.inference.groq import ChatGroq
        print("✅ Groq API available")
        return ChatGroq(), "groq"
    except Exception as e:
        print(f"❌ Groq failed: {e}")
    
    # Option 2: Try Ollama local
    try:
        from src.inference.ollama import ChatOllama
        import requests
        # Quick health check
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama local available")
            return ChatOllama(model="llama3.2"), "ollama"
        else:
            print("❌ Ollama server not running")
    except Exception as e:
        print(f"❌ Ollama failed: {e}")
    
    # Option 3: No LLM (use keyword routing)
    print("⚠️  Using fallback mode (no LLM)")
    return None, "fallback"

def test_mcp_with_fallback():
    """Test MCP tools với fallback LLM options"""
    
    print("🧪 Testing MCP Tools with Rate Limit Protection")
    print("=" * 60)
    
    # Get best available LLM
    llm, llm_type = get_available_llm()
    print(f"\n🔧 Using LLM: {llm_type}")
    
    # Create MCPToolAgent
    agent = MCPToolAgent(llm=llm, verbose=True)
    
    # Test queries
    test_queries = [
        "list all available tools",
        "get device list from living room", 
        "help with smart home controls"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 40)
        
        try:
            if llm_type == "groq":
                print("⏱️  Adding rate limit delay for Groq...")
                time.sleep(3)  # Extra delay for Groq
            
            state = AgentState(input=query)
            result = agent.invoke(query)
            
            output = result.get('output', 'No output')
            route = result.get('route', 'No route')
            
            print(f"Route: {route}")
            print(f"Output length: {len(output)}")
            print(f"Output preview: {output[:150]}...")
            
            if len(output) > 50:
                print("✅ SUCCESS")
            else:
                print("❌ FAILED - Empty response")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            if "429" in str(e):
                print("⏱️  Rate limit hit - waiting 60 seconds...")
                time.sleep(60)
            continue

def quick_mcp_test():
    """Quick test without LLM to verify MCP connection"""
    
    print("\n🔍 Quick MCP Connection Test (No LLM)")
    print("=" * 40)
    
    try:
        agent = MCPToolAgent(llm=None, verbose=True)
        
        # Direct tool listing
        state = AgentState(input='list tools')
        result = agent.list_tools(state)
        output = result.get('output', '')
        
        if 'get_device_list' in output and len(output) > 200:
            print("✅ MCP Connection: SUCCESS")
            print(f"Found {output.count('**')} tools")
            return True
        else:
            print("❌ MCP Connection: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ MCP Error: {e}")
        return False

if __name__ == "__main__":
    print("🏠 MCP Smart Home Tool Agent Test")
    print("=" * 60)
    
    # Quick test first
    if quick_mcp_test():
        print("\n" + "="*60)
        test_mcp_with_fallback()
    else:
        print("\n❌ Basic MCP connection failed, please check MCP server")
        sys.exit(1)