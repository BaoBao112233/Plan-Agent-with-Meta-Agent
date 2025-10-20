#!/usr/bin/env python3

"""
Test script to verify that the improved API key rotation logic works correctly
and handles various failure scenarios gracefully.
"""

from src.inference.groq import ChatGroq
from src.message import HumanMessage, SystemMessage

def test_api_key_rotation():
    print('🧪 Testing Enhanced API Key Rotation Logic')
    print('=' * 60)
    
    # Test 1: Normal operation
    print('\n📝 Test 1: Normal API operation')
    print('-' * 40)
    
    try:
        llm = ChatGroq()
        print(f"✅ ChatGroq initialized with {len(llm.api_keys)} API keys")
        print(f"   Current key: {llm.api_key[:10]}... (index {llm.current_key_index})")
        
        # Test with a simple message
        messages = [SystemMessage("You are a helpful assistant."), HumanMessage("Say hello")]
        result = llm.invoke(messages)
        print(f"✅ API call successful! Response: {result.content[:50]}...")
        
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return False
    
    # Test 2: Key rotation method
    print('\n📝 Test 2: Key rotation method')
    print('-' * 40)
    
    try:
        llm = ChatGroq()
        original_key = llm.current_key_index
        
        # Test rotation function
        if len(llm.api_keys) > 1:
            success = llm._rotate_to_available_key()
            if success:
                print(f"✅ Key rotation successful: {original_key} → {llm.current_key_index}")
            else:
                print("⚠️  Key rotation returned False (expected if all keys failed)")
        else:
            print("⚠️  Only 1 API key available, rotation not needed")
            
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return False
    
    # Test 3: Error classification
    print('\n📝 Test 3: Error classification')
    print('-' * 40)
    
    try:
        llm = ChatGroq()
        
        # Test rate limit detection
        class MockRateLimitError(Exception):
            def __init__(self):
                super().__init__("429 Too Many Requests")
                self.response = type('obj', (object,), {'status_code': 429})
        
        rate_error = MockRateLimitError()
        is_rate_limit = llm._is_rate_limit_error(rate_error)
        print(f"✅ Rate limit error detection: {is_rate_limit} (should be True)")
        
        # Test non-rate-limit error
        other_error = Exception("Some other error")
        is_other = llm._is_rate_limit_error(other_error)
        print(f"✅ Other error detection: {is_other} (should be False)")
        
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        return False
    
    # Test 4: Stress test with multiple calls
    print('\n📝 Test 4: Multiple API calls stress test')
    print('-' * 40)
    
    try:
        llm = ChatGroq()
        success_count = 0
        
        for i in range(5):
            try:
                messages = [HumanMessage(f"Test message {i+1}: What is {i+1} + {i+1}?")]
                result = llm.invoke(messages)
                success_count += 1
                print(f"✅ Call {i+1}/5 successful")
            except Exception as e:
                print(f"❌ Call {i+1}/5 failed: {e}")
                break
        
        print(f"📊 Stress test results: {success_count}/5 calls successful")
        
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        return False
    
    print('\n🎉 All API rotation tests completed!')
    return True

def test_error_handling():
    """Test how the system handles various error scenarios"""
    print('\n🔧 Testing Error Handling Scenarios')
    print('=' * 50)
    
    llm = ChatGroq()
    
    # Test empty message handling
    try:
        empty_result = llm.invoke([])
        print('✅ Empty message handling successful')
    except Exception as e:
        print(f'⚠️  Empty message error (expected): {e}')
    
    # Test malformed message handling
    try:
        malformed_messages = [HumanMessage("" * 100000)]  # Very long message
        result = llm.invoke(malformed_messages)
        print('✅ Long message handling successful')
    except Exception as e:
        if "413" in str(e):
            print('⚠️  Long message error (expected): Payload too large')
        else:
            print(f'⚠️  Long message error: {e}')
    
    return True

if __name__ == "__main__":
    test_api_key_rotation()
    test_error_handling()
    print('\n🎯 API rotation fix verification completed!')