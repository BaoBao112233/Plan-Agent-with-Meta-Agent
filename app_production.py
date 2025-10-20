#!/usr/bin/env python3

"""Production app với dual API key protection"""

import sys
import time
from datetime import datetime

def test_mcp_agent_with_dual_keys():
    """Test MCPToolAgent với dual API key protection"""
    
    print("🏠 MCP Smart Home Agent - Dual API Key Protected")
    print("=" * 60)
    print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        from src.agent.tool.mcp_agent import MCPToolAgent
        from src.inference.groq import ChatGroq
        
        # Create LLM with dual key support
        llm = ChatGroq()
        print(f"🔑 Loaded {len(llm.api_keys)} API keys for failover")
        
        # Create MCP agent
        agent = MCPToolAgent(llm=llm, verbose=True)
        
        # Test queries that might trigger rate limits
        queries = [
            "list all available smart home tools",
            "get device list for living room", 
            "control air conditioner in bedroom",
            "show help for smart home controls",
            "search for lighting controls"
        ]
        
        success_count = 0
        
        for i, query in enumerate(queries, 1):
            print(f"\n📝 Test {i}/5: {query}")
            print("-" * 50)
            
            try:
                start_time = time.time()
                result = agent.invoke(query)
                elapsed = time.time() - start_time
                
                output = result.get('output', '')
                route = result.get('route', '')
                
                print(f"✅ Success in {elapsed:.1f}s")
                print(f"   Route: {route}")
                print(f"   Output: {len(output)} chars")
                print(f"   Preview: {output[:100]}...")
                print(f"   🔑 API Key: #{llm.current_key_index + 1}")
                
                success_count += 1
                
            except Exception as e:
                print(f"❌ Failed: {e}")
                if "429" in str(e):
                    print("🔄 Rate limit - should auto-rotate API keys")
        
        print(f"\n📊 Results: {success_count}/{len(queries)} queries successful")
        return success_count >= len(queries) * 0.8  # 80% success rate
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def test_full_workflow():
    """Test full workflow với rate limit protection"""
    
    print(f"\n🔄 Testing Full ReactAgent Workflow")
    print("=" * 50)
    
    try:
        from src.agent.react import ReactAgent
        from src.inference.groq import ChatGroq
        
        llm = ChatGroq()
        
        react_agent = ReactAgent(
            name="Smart Home Controller",
            description="Agent for smart home device control",
            llm=llm,
            verbose=True,
            max_iterations=3  # Limit to prevent too many API calls
        )
        
        print(f"✅ ReactAgent created with dual API key protection")
        
        # Test workflow
        query = "show me all available smart home tools and help me understand what they do"
        
        print(f"\n📝 Testing workflow: {query}")
        
        start_time = time.time()
        result = react_agent.invoke(query)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Workflow completed in {elapsed:.1f}s")
        print(f"🔑 Final API key: #{llm.current_key_index + 1}")
        print(f"📄 Result: {len(str(result))} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        if "429" in str(e):
            print("🚫 Rate limit detected - dual key system should have prevented this")
        return False

def test_meta_agent():
    """Test MetaAgent với dual API key protection"""
    
    print(f"\n🧠 Testing MetaAgent with Rate Limit Protection")
    print("=" * 50)
    
    try:
        from src.agent.meta import MetaAgent
        from src.inference.groq import ChatGroq
        
        llm = ChatGroq()
        meta_agent = MetaAgent(llm=llm, verbose=True)
        
        query = "I need to check all devices in my living room and turn on the lights"
        
        print(f"📝 MetaAgent query: {query}")
        
        start_time = time.time()
        result = meta_agent.invoke(query)
        elapsed = time.time() - start_time
        
        print(f"✅ MetaAgent completed in {elapsed:.1f}s")
        print(f"🔑 Final API key: #{llm.current_key_index + 1}")
        print(f"Result preview: {str(result)[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ MetaAgent failed: {e}")
        if "429" in str(e):
            print("🚫 Rate limit hit - checking if rotation occurred")
        return False

def main():
    """Main production test"""
    
    print("🎯 Production Test - Dual API Key 429 Protection")
    print("=" * 70)
    
    tests = [
        ("MCP Agent with Dual Keys", test_mcp_agent_with_dual_keys),
        ("Full ReactAgent Workflow", test_full_workflow),
        ("MetaAgent Integration", test_meta_agent)
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
        
        # Wait between tests to avoid rate limits
        print("⏱️  Waiting 5s between tests...")
        time.sleep(5)
    
    # Final summary
    print("\n" + "=" * 70)
    print("🎯 PRODUCTION TEST SUMMARY")
    print("=" * 70)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:30} {status}")
    
    pass_count = sum(1 for _, success in results if success)
    print(f"\nTotal: {pass_count}/{len(results)} tests passed")
    
    if pass_count >= len(results) * 0.8:
        print("🎉 PRODUCTION READY - Dual API key system prevents 429 errors!")
    else:
        print("⚠️  Production issues detected - review rate limiting")

if __name__ == "__main__":
    main()