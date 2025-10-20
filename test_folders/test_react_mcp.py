#!/usr/bin/env python3

"""Test ReactAgent tool_agent với MCPToolAgent integration"""

from src.agent.react import ReactAgent
from src.agent.react.state import AgentState
from src.agent.react.utils import extract_llm_response
from src.message import HumanMessage, AIMessage

def test_react_agent_tool_integration():
    """Test ReactAgent tool_agent method với MCPToolAgent"""
    
    print("🧪 Testing ReactAgent tool_agent integration")
    print("=" * 50)
    
    # Create ReactAgent without LLM to avoid API issues
    react_agent = ReactAgent(llm=None, verbose=True)
    
    # Create fake state như ReactAgent sẽ nhận từ LLM response  
    fake_llm_response = """
    <Thought>User wants to see available tools, I should route to tool agent</Thought>
    <Query>list all available tools</Query>
    <Route>tool</Route>
    """
    
    # Tạo state với message có response format như ReactAgent expect
    state = AgentState(
        input='list tools',
        messages=[AIMessage(fake_llm_response)],
        output=''
    )
    
    print("🔸 Calling ReactAgent.tool_agent()...")
    
    try:
        result = react_agent.tool_agent(state)
        messages = result.get('messages', [])
        
        if messages:
            last_message = messages[-1]
            content = last_message.content
            print(f"\n✅ ReactAgent tool_agent response:")
            print(f"Message type: {type(last_message)}")
            print(f"Content length: {len(content)}")
            print(f"First 200 chars: {content[:200]}...")
            
            if 'Available MCP Tools' in content and len(content) > 100:
                print("\n🎯 SUCCESS: ReactAgent correctly integrated with MCPToolAgent!")
                return True
            else:
                print("\n❌ FAILED: Response format incorrect")
                print(f"Full content: {content}")
                return False
        else:
            print("\n❌ FAILED: No messages in result")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR in tool_agent: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_react_agent_tool_integration()
    print(f"\n🎯 Final Result: {'SUCCESS' if success else 'FAILED'}")