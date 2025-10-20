#!/usr/bin/env python3
"""
Simple test để debug router issue
"""

from src.router import LLMRouter
from src.inference.groq import ChatGroq

def test_router_directly():
    """Test router trực tiếp để debug"""
    print("🔍 Testing Router Directly...")
    
    llm = ChatGroq()
    
    routes = [
        {
            'route': 'simple',
            'description': 'This route handles straightforward tasks with no user interaction.'
        },
        {
            'route': 'advanced', 
            'description': 'This route is tailored for more complex, involved or ambiguous tasks.'
        },
        {
            'route': 'priority',
            'description': 'This route creates 3 alternative plans prioritized by Security, Convenience, and Energy Efficiency.'
        }
    ]
    
    router = LLMRouter(routes=routes, llm=llm, verbose=True)
    
    test_queries = [
        "Create a simple backup script",
        "Design a smart home system with multiple priorities and considerations",
        "Build an IoT system focusing on security, convenience and energy efficiency"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        try:
            route = router.invoke(query)
            print(f"   ✅ Result: {route}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_router_directly()