#!/usr/bin/env python3
"""
Debug environment variable loading and API key usage.
"""

import os
import requests
from dotenv import load_dotenv

def debug_environment():
    """Debug environment variable loading."""
    
    print("🔍 Environment Debug Information\n")
    
    # Check if .env file exists
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ .env file exists: {env_file}")
        with open(env_file, 'r') as f:
            content = f.read()
            print(f"📄 .env file content length: {len(content)} characters")
    else:
        print(f"❌ .env file not found: {env_file}")
    
    # Check environment before loading .env
    print(f"\n🔍 OPENAI_API_KEY before load_dotenv(): {os.getenv('OPENAI_API_KEY', 'NOT SET')[:20] if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
    
    # Load .env
    load_result = load_dotenv()
    print(f"📥 load_dotenv() result: {load_result}")
    
    # Check environment after loading .env
    api_key_after = os.getenv('OPENAI_API_KEY')
    print(f"🔍 OPENAI_API_KEY after load_dotenv(): {api_key_after[:20] if api_key_after else 'NOT SET'}...")
    
    # Check if there are any other OpenAI-related env vars
    openai_vars = {k: v for k, v in os.environ.items() if 'OPENAI' in k.upper()}
    print(f"\n🔍 All OpenAI-related environment variables:")
    for key, value in openai_vars.items():
        print(f"   {key}: {value[:20] if value else 'EMPTY'}...")
    
    return api_key_after

def test_with_explicit_key():
    """Test with the exact key from the curl command."""
    
    # The exact key from your curl command
    explicit_key = "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"
    
    print(f"\n🔄 Testing with explicit key from curl command...")
    print(f"🔑 Key: {explicit_key[:20]}...")
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {explicit_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Hello!"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS with explicit key!")
            print(f"📝 Response: {result['choices'][0]['message']['content']}")
            print(f"💰 Tokens: {result['usage']['total_tokens']}")
            return True
        else:
            print(f"❌ FAILED with explicit key:")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR with explicit key: {e}")
        return False

def test_curl_simulation():
    """Test by exactly simulating the curl command."""
    
    print(f"\n🔄 Simulating exact curl command...")
    
    # Try to run the exact curl command that worked
    import subprocess
    
    curl_cmd = [
        'curl', 'https://api.openai.com/v1/chat/completions',
        '-H', 'Authorization: Bearer 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',
        '-H', 'Content-Type: application/json',
        '-d', '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello!"}], "max_tokens": 10}'
    ]
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
        print(f"📊 Curl exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Curl command succeeded!")
            print(f"📝 Response: {result.stdout[:200]}...")
            return True
        else:
            print("❌ Curl command failed!")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR running curl: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Debugging API key and environment issues...\n")
    
    # Debug environment
    api_key = debug_environment()
    
    # Test with explicit key
    explicit_works = test_with_explicit_key()
    
    # Test curl simulation
    curl_works = test_curl_simulation()
    
    print(f"\n📊 Results:")
    print(f"   Environment API key: {'✅' if api_key else '❌'}")
    print(f"   Explicit key test:   {'✅' if explicit_works else '❌'}")
    print(f"   Curl simulation:     {'✅' if curl_works else '❌'}")
    
    if curl_works and not explicit_works:
        print("\n🤔 Curl works but Python doesn't - this suggests a Python/requests issue")
    elif not curl_works:
        print("\n🤔 Even curl is failing now - the quota might have been exhausted")
