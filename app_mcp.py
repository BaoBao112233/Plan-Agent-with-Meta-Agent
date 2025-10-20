"""
Enhanced app.py với MCP integration cho MetaAgent
"""

from src.agent.meta import MetaAgent
from src.agent.plan import PlanAgent
from src.agent.tool import MCPToolAgent
from src.inference.groq import ChatGroq
from src.mcp_tools import get_mcp_tools, list_mcp_tool_names
from os import environ
from dotenv import load_dotenv
from experimental import *

load_dotenv()

def create_meta_agent_with_mcp_tools():
    """Tạo MetaAgent với MCP tools"""
    api_key = environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")
    
    llm = ChatGroq('llama-3.3-70b-versatile', api_key, temperature=0)
    
    # Load MCP tools
    try:
        mcp_tools = get_mcp_tools()
        mcp_tool_names = list_mcp_tool_names()
        print(f"✅ Loaded {len(mcp_tools)} MCP tools: {', '.join(mcp_tool_names)}")
    except Exception as e:
        print(f"⚠️  Warning: Could not load MCP tools: {e}")
        print("MetaAgent will run without MCP tools.")
        mcp_tools = []
    
    # Add experimental tools
    experimental_tools = [web_search_tool, file_writer_tool, system_time_tool, current_time_tool]
    all_tools = experimental_tools + mcp_tools
    
    meta_agent = MetaAgent(
        llm=llm,
        tools=all_tools,
        verbose=True
    )
    
    return meta_agent

def test_meta_agent_with_mcp():
    """Test MetaAgent với MCP tools"""
    print("🤖 Testing MetaAgent with MCP Tools")
    print("=" * 60)
    
    try:
        meta_agent = create_meta_agent_with_mcp_tools()
        
        print("\n🔧 Available tools in MetaAgent:")
        for i, tool in enumerate(meta_agent.tools, 1):
            tool_name = getattr(tool, 'name', getattr(tool, '__name__', 'Unknown'))
            print(f"  {i}. {tool_name}")
        
        print("\n" + "-" * 60)
        user_input = input("Enter a query for MetaAgent with MCP tools: ")
        
        print("\n🚀 Executing with MetaAgent...")
        response = meta_agent.invoke(user_input)
        
        print("\n" + "="*60)
        print("Final Response:")
        print(response)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_plan_agent_with_mcp_meta():
    """Test Plan Agent với MetaAgent có MCP tools"""
    print("\n📋 Testing Plan Agent with MCP-enabled MetaAgent")
    print("=" * 60)
    
    try:
        api_key = environ.get("GROQ_API_KEY")
        llm = ChatGroq('llama-3.3-70b-versatile', api_key, temperature=0)
        
        # Plan Agent sẽ sử dụng MetaAgent internally, 
        # và MetaAgent sẽ có access đến MCP tools
        plan_agent = PlanAgent(llm=llm, verbose=True, api_enabled=True)
        
        print("Plan Agent ready with:")
        print("- ✅ API integration (http://localhost:8000)")
        print("- ✅ MCP tools via MetaAgent")
        print("- ✅ Experimental tools")
        
        print("\n" + "-" * 60)
        user_input = input("Enter a query for Plan Agent: ")
        
        print("\n🚀 Executing Plan Agent...")
        response = plan_agent.invoke(user_input)
        
        print("\n" + "="*60)
        print("Final Response:")
        print(response)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main application"""
    print("🚀 Plan Agent with MCP Integration")
    print("=" * 60)
    
    # Check MCP server status
    try:
        import requests
        response = requests.get("http://localhost:9031/sse", timeout=5)
        if response.status_code == 200:
            print("✅ MCP Server is running at http://localhost:9031")
        else:
            print("⚠️  MCP Server might not be responding properly")
    except Exception as e:
        print(f"❌ MCP Server connection failed: {e}")
        print("Some features may not work without MCP server.")
    
    print("\nChoose an option:")
    print("1. Test MCP Tool Agent directly")
    print("2. Test MetaAgent with MCP tools")
    print("3. Test Plan Agent (full integration)")
    print("4. All tests")
    
    choice = input("\nEnter your choice (1/2/3/4): ").strip()
    
    if choice == "1":
        # Test direct MCP Tool Agent
        api_key = environ.get("GROQ_API_KEY")
        llm = ChatGroq('llama-3.3-70b-versatile', api_key, temperature=0)
        tool_agent = MCPToolAgent(llm=llm, verbose=True)
        
        user_input = input("Query for MCP Tool Agent: ")
        response = tool_agent.invoke(user_input)
        print(f"Response: {response}")
        
    elif choice == "2":
        test_meta_agent_with_mcp()
        
    elif choice == "3":
        test_plan_agent_with_mcp_meta()
        
    elif choice == "4":
        print("\n🧪 Running all tests...")
        test_meta_agent_with_mcp()
        test_plan_agent_with_mcp_meta()
        
    else:
        print("❌ Invalid choice. Running Plan Agent by default...")
        test_plan_agent_with_mcp_meta()

if __name__ == "__main__":
    main()