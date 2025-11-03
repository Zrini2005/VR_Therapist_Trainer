"""
Test script for VR-Therapist server
Tests the server endpoints without requiring audio files
"""

import requests
import json

SERVER_URL = "http://127.0.0.1:5000"

def test_check_status():
    """Test the /check_status endpoint"""
    print("\n=== Testing /check_status endpoint ===")
    try:
        response = requests.get(f"{SERVER_URL}/check_status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_reset_conversation():
    """Test the /reset_conversation endpoint"""
    print("\n=== Testing /reset_conversation endpoint ===")
    try:
        data = {"reset_conversation": "yes"}
        response = requests.post(f"{SERVER_URL}/reset_conversation", data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_process_wav():
    """Test the /process_wav endpoint"""
    print("\n=== Testing /process_wav endpoint ===")
    try:
        data = {
            "path": "C:/test/",
            "loaded_wav_file": "patient_speech"
        }
        response = requests.post(f"{SERVER_URL}/process_wav", data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_huggingface_api():
    """Test Hugging Face API connection"""
    print("\n=== Testing Hugging Face API ===")
    try:
        from therapy_session import initialize_client, generate_therapist_response
        
        # Read config
        with open('config.json') as f:
            config = json.load(f)
        
        client = initialize_client(config['HF_TOKEN'])
        print("✓ Hugging Face client initialized")
        
        # Test simple prompt
        prompt = "Hello, how are you?"
        print(f"Sending test prompt: '{prompt}'")
        
        response = generate_therapist_response(
            client=client,
            prompt_message=prompt,
            hf_token=config['HF_TOKEN'],
            model_name=config.get('MODEL_NAME', 'meta-llama/Meta-Llama-3-8B-Instruct')
        )
        
        print(f"✓ Response received: {response[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("VR-Therapist Server Test Suite")
    print("=" * 60)
    print(f"Server URL: {SERVER_URL}")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{SERVER_URL}/check_status", timeout=2)
        print("✓ Server is running!")
    except Exception as e:
        print(f"❌ Server is not responding. Make sure it's running on {SERVER_URL}")
        print(f"   Error: {e}")
        return
    
    # Run tests
    results = {
        "check_status": test_check_status(),
        "reset_conversation": test_reset_conversation(),
        "process_wav": test_process_wav(),
        "huggingface_api": test_huggingface_api()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! Server is working correctly.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check the errors above.")

if __name__ == "__main__":
    main()
