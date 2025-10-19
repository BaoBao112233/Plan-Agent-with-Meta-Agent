from src.agent.meta import MetaAgent
from src.agent.plan import PlanAgent
from src.agent.tool import ToolAgent  # Now imports MCPToolAgent
from src.mcp_tools_wrapper import get_mcp_tools_for_meta_agent
from src.inference.groq import ChatGroq
from os import environ
from dotenv import load_dotenv
from experimental import *

load_dotenv()

def test_mcp_tool_agent():
    """Test MCP Tool Agent functionality"""
    print("🔧 Testing MCP Tool Agent")
    print("=" * 50)
    
    api_key = environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please add it to your .env file.")
    
    llm = ChatGroq('llama-3.3-70b-versatile', api_key, temperature=0)
    
    # Initialize MCP Tool Agent
    tool_agent = ToolAgent(llm=llm, verbose=True)
    
    print("\n🔍 Available commands:")
    print("1. 'list tools' - Show all available MCP tools")
    print("2. 'search [keyword]' - Search for specific tools")
    print("3. 'info [tool_name]' - Get detailed tool information")
    print("4. 'execute [tool_name] with [parameters]' - Execute a tool")
    print("5. 'help' - Get general help")
    print("-" * 50)
    
    while True:
        user_input = input("\nMCP Tool Agent Query (or 'quit' to exit): ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        try:
            response = tool_agent.invoke(user_input)
            print(f"\n📋 Route: {response.get('route', 'unknown')}")
            print(f"🎯 Response:\n{response.get('output', 'No output')}")
            print(f"🔧 Available Tools: {response.get('available_tools', 0)}")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_meta_agent_with_mcp():
    """Test MetaAgent với MCP tools"""
    print("\n🧠 Testing MetaAgent with MCP Tools")
    print("=" * 50)
    
    api_key = environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please add it to your .env file.")
    
    llm = ChatGroq('llama-3.3-70b-versatile', api_key, temperature=0)
    
    # Load MCP tools for MetaAgent
    try:
        mcp_tools = get_mcp_tools_for_meta_agent()
        print(f"✅ Loaded {len(mcp_tools)} MCP tools for MetaAgent:")
        for tool in mcp_tools:
            print(f"  - {tool.name}")
    except Exception as e:
        print(f"❌ Error loading MCP tools: {e}")
        mcp_tools = []
    
    # Initialize MetaAgent with MCP tools
    meta_agent = MetaAgent(llm=llm, tools=mcp_tools, verbose=True)
    
    print("\n📝 Example queries for MetaAgent with MCP tools:")
    print("- 'Get list of all devices in the system'")
    print("- 'Turn on the living room lights'")
    print("- 'Set air conditioner to cool mode at 24 degrees'")
    print("- 'Turn off all devices in the house'")
    print("-" * 50)
    
    user_input = input("\nEnter a query for MetaAgent: ")
    
    try:
        agent_response = meta_agent.invoke(user_input)
        print(f"\n🎯 MetaAgent Response:\n{agent_response}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_plan_agent():
    """Test Plan Agent with MCP integration through MetaAgent"""
    print("\n🤖 Testing Plan Agent with MCP integration")
    print("=" * 50)
    
    api_key = environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please add it to your .env file.")
    
    llm = ChatGroq('llama-3.3-70b-versatile', api_key, temperature=0)
    
    # Initialize Plan Agent with API enabled
    plan_agent = PlanAgent(llm=llm, verbose=True, api_enabled=True)
    
    print("Plan Agent đã sẵn sàng!")
    print("- API integration: ✅ Enabled (sends to http://localhost:8000)")
    print("- MCP tools: ✅ Available through MetaAgent in execution steps")
    print("\n📝 Example Plan Agent queries:")
    print("- 'Create a plan to control my smart home devices'")
    print("- 'Plan to set up evening mode in my house'")
    print("- 'Create a schedule for automatically controlling AC'")
    print("-" * 50)
    
    user_input = input("Enter a query for Plan Agent: ")
    agent_response = plan_agent.invoke(user_input)
    
    print("\n" + "="*50)
    print("Final Response:")
    print(agent_response)

def main():
    """Main application entry point"""
    print("🚀 Plan Agent with MCP Integration")
    print("=" * 50)
    print("Choose an option:")
    print("1. Test MCP Tool Agent directly")
    print("2. Test MetaAgent with MCP tools")  
    print("3. Test Plan Agent (with MCP tools via MetaAgent)")
    print("4. All tests")
    
    choice = input("\nEnter your choice (1/2/3/4): ").strip()
    
    if choice == "1":
        test_mcp_tool_agent()
    elif choice == "2":
        test_meta_agent_with_mcp()
    elif choice == "3":
        test_plan_agent()
    elif choice == "4":
        test_mcp_tool_agent()
        test_meta_agent_with_mcp()
        test_plan_agent()
    else:
        print("❌ Invalid choice. Starting Plan Agent by default...")
        test_plan_agent()

if __name__ == "__main__":
    main()