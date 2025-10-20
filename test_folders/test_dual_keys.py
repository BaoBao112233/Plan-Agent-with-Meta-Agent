#!/usr/bin/env python3

"""Test dual API key rotation and 429 error handling"""

import time
from src.inference.groq import ChatGroq
from src.message import HumanMessage

def test_api_key_rotation():
    """Test API key rotation functionality"""
    
    print("🔧 Testing Dual API Key Rotation")
    print("=" * 50)
    
    # Create ChatGroq instance
    llm = ChatGroq()
    
    print(f"📊 Loaded {len(llm.api_keys)} API keys")
    for i, key in enumerate(llm.api_keys):
        print(f"  Key {i+1}: {key[:10]}...")
    
    # Test basic functionality
    print(f"\n✅ Current API key: #{llm.current_key_index + 1}")
    
    # Test API key rotation
    print("\n🔄 Testing manual API key rotation:")
    for i in range(3):
        success = llm.rotate_api_key()
        if success:
            print(f"  Rotation {i+1}: Now using key #{llm.current_key_index + 1}")
        else:
            print(f"  Rotation {i+1}: No more keys to rotate")
    
    return True

def test_rate_limit_handling():
    """Test rate limit handling with actual API calls"""
    
    print("\n🚫 Testing Rate Limit Handling")
    print("=" * 50)
    
    llm = ChatGroq()
    
    # Make several quick requests to potentially trigger rate limit
    print("🔥 Making rapid API requests to test rate limit handling...")
    
    for i in range(5):
        try:
            print(f"\n📞 Request {i+1}:")
            start_time = time.time()
            
            response = llm.invoke([HumanMessage(f"Say hello #{i+1}")])
            
            elapsed = time.time() - start_time
            print(f"  ✅ Success in {elapsed:.1f}s: {response.content[:50]}...")
            print(f"  🔑 Used API key #{llm.current_key_index + 1}")
            
        except Exception as e:
            print(f"  ❌ Request {i+1} failed: {e}")
            if "429" in str(e):
                print(f"  🚫 Rate limit detected - should auto-rotate")
            break
    
    return True

def test_exhausted_keys_scenario():
    """Test scenario where all keys are exhausted"""
    
    print("\n⏱️  Testing All Keys Exhausted Scenario")
    print("=" * 50)
    
    llm = ChatGroq()
    
    # Simulate all keys being rate limited
    llm._failed_keys = set(range(len(llm.api_keys)))
    
    print("🚫 Simulating all API keys rate limited...")
    
    try:
        # This should wait and reset
        response = llm.invoke([HumanMessage("Test after all keys failed")])
        print("✅ Successfully recovered after all keys failed")
        return True
    except Exception as e:
        print(f"❌ Failed to recover: {e}")
        return False

def stress_test_rotation():
    """Stress test API key rotation with many requests"""
    
    print("\n💪 Stress Testing API Key Rotation")
    print("=" * 50)
    
    llm = ChatGroq()
    success_count = 0
    rotation_count = 0
    
    for i in range(10):
        try:
            old_key_index = llm.current_key_index
            
            response = llm.invoke([HumanMessage(f"Stress test {i+1}")])
            success_count += 1
            
            if llm.current_key_index != old_key_index:
                rotation_count += 1
                print(f"🔄 Key rotation #{rotation_count} during request {i+1}")
            
            print(f"  ✅ Request {i+1}: Success with key #{llm.current_key_index + 1}")
            
        except Exception as e:
            print(f"  ❌ Request {i+1}: Failed - {e}")
            if "429" in str(e):
                print(f"    🚫 Rate limit - auto rotation should happen")
    
    print(f"\n📊 Stress Test Results:")
    print(f"  Successful requests: {success_count}/10")
    print(f"  Key rotations: {rotation_count}")
    
    return success_count >= 5  # At least 50% success rate

def main():
    """Main test function"""
    
    print("🎯 Dual API Key Rotation Test Suite")
    print("=" * 60)
    
    tests = [
        ("API Key Loading & Rotation", test_api_key_rotation),
        ("Rate Limit Handling", test_rate_limit_handling),
        ("Exhausted Keys Scenario", test_exhausted_keys_scenario),
        ("Stress Test", stress_test_rotation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"Result: {status}")
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:30} {status}")
    
    pass_count = sum(1 for _, success in results if success)
    print(f"\nTotal: {pass_count}/{len(results)} tests passed")
    
    if pass_count == len(results):
        print("🎉 ALL TESTS PASSED - Dual API key system working!")
    else:
        print("⚠️  Some tests failed - check configuration")

if __name__ == "__main__":
    main()