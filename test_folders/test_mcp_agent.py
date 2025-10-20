#!/usr/bin/env python3
"""
Test script cho MCP Tool Agent
"""

from src.agent.tool.mcp_agent import MCPToolAgent
from src.inference.groq import ChatGroq
from dotenv import load_dotenv
from os import environ

load_dotenv()

def test_mcp_agent():
    """Test MCP Tool Agent"""
    print("🧪 Testing MCP Tool Agent...")
    
    # Setup LLM
    api_key = environ.get("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found")
        return
    
    llm = ChatGroq('llama-3.3-70b-versatile', api_key, temperature=0)
    agent = MCPToolAgent(llm=llm, verbose=True)
    
    # Test queries
    test_queries = [
        "list of devices",
        "turn on all lights",
        "get device list with token abc123",
        "control air conditioner temperature 24 degrees cooling mode"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"🔍 Query: {query}")
        print('='*60)
        
        try:
            response = agent.invoke(query)
            print(f"✅ Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 60)

if __name__ == "__main__":
    test_mcp_agent()