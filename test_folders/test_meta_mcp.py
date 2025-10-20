#!/usr/bin/env python3

"""Test MetaAgent với MCPToolAgent integration"""

import sys
sys.path.append('.')

from src.agent.meta import MetaAgent  
from src.agent.meta.state import AgentState

def test_meta_agent_with_mcp():
    """Test MetaAgent routing to MCPToolAgent"""
    
    print("🧪 Testing MetaAgent with MCP Tools")
    print("=" * 50)
    
    # Create MetaAgent without LLM để avoid API issues
    meta_agent = MetaAgent(llm=None, verbose=True)
    
    try:
        print("🔸 Testing MetaAgent.invoke() for tool listing...")
        
        # Use invoke method directly
        result = meta_agent.invoke('list all available smart home tools')
        
        print(f"\n✅ MetaAgent result:")
        print(f"Type: {type(result)}")
        print(f"Length: {len(str(result))}")
        print(f"Content: {str(result)[:300]}...")
        
        if 'Available MCP Tools' in str(result) and 'get_device_list' in str(result):
            print("\n🎯 SUCCESS: MetaAgent correctly integrated with MCP tools!")
            return True
        else:
            print("\n❌ FAILED: Response doesn't contain expected MCP tools")
            print(f"Full result: {result}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR in MetaAgent: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_meta_agent_with_mcp()
    print(f"\n🎯 Final Result: {'SUCCESS' if success else 'FAILED'}")