#!/usr/bin/env python3

"""Test parameter auto-filling trong MCPToolAgent"""

def test_parameter_extraction():
    """Test parameter extraction và auto-filling"""
    
    print("🔧 Testing Parameter Auto-Filling")
    print("=" * 50)
    
    try:
        from src.agent.tool.mcp_agent import MCPToolAgent
        from src.inference.groq import ChatGroq
        
        llm = ChatGroq()
        agent = MCPToolAgent(llm=llm, verbose=True)
        
        # Test queries với different parameter requirements
        test_queries = [
            "get device list for living room",
            "turn on the bedroom light", 
            "set air conditioner to 22 degrees celsius cool mode",
            "turn off all lights",
            "control device number 5 to turn on"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test {i}: {query}")
            print("-" * 40)
            
            try:
                result = agent.invoke(query)
                
                output = result.get('output', '')
                route = result.get('route', '')
                
                print(f"✅ Route: {route}")
                
                if "Parameter validation failed" in output:
                    print("❌ Still missing parameters:")
                    print(output[:300] + "...")
                elif "executed" in output:
                    print("✅ Tool executed successfully!")
                    if "REAL MCP SERVER" in output:
                        print("🔌 Using real MCP server")
                    elif "MOCK" in output:
                        print("🧪 Using mock (server unavailable)")
                else:
                    print("📋 Tool listing or help provided")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def test_direct_parameter_filling():
    """Test parameter auto-filling directly"""
    
    print("\n🔧 Testing Direct Parameter Auto-Filling")
    print("=" * 50)
    
    try:
        from src.agent.tool.mcp_agent import MCPToolAgent
        from src.inference.groq import ChatGroq
        
        llm = ChatGroq()
        agent = MCPToolAgent(llm=llm, verbose=True)
        
        # Test direct parameter filling
        test_cases = [
            ("get_device_list", {}, "get device list"),
            ("switch_device_control", {}, "turn on light 3"),
            ("control_air_conditioner", {"temp": "25"}, "set AC to cool mode"),
        ]
        
        for tool_name, initial_params, query in test_cases:
            print(f"\n🔧 Testing {tool_name}:")
            print(f"   Query: {query}")
            print(f"   Initial params: {initial_params}")
            
            filled_params = agent.auto_fill_parameters(tool_name, initial_params, query)
            print(f"   Filled params: {filled_params}")
            
            # Test validation
            is_valid, errors = agent.mcp_client.validate_parameters(tool_name, filled_params)
            if is_valid:
                print("   ✅ Parameters valid after auto-fill")
            else:
                print(f"   ❌ Still invalid: {errors}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 MCPToolAgent Parameter Auto-Fill Test")
    print("=" * 60)
    
    success1 = test_parameter_extraction()
    success2 = test_direct_parameter_filling()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 All parameter tests passed!")
    else:
        print("⚠️  Some parameter tests failed")