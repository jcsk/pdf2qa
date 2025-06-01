#!/usr/bin/env python3
"""
Test OpenAI API exactly like the working curl command.
"""

import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

def test_with_requests():
    """Test using requests library (like curl)."""
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    print("🔄 Testing with requests library (like curl)...")
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
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
            print("✅ SUCCESS with requests!")
            print(f"📝 Response: {result['choices'][0]['message']['content']}")
            print(f"💰 Tokens: {result['usage']['total_tokens']}")
            return True
        else:
            print(f"❌ FAILED with requests: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR with requests: {e}")
        return False

def test_with_openai_lib():
    """Test using OpenAI library."""
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    print("\n🔄 Testing with OpenAI library...")
    
    try:
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello!"}],
            max_tokens=10
        )
        
        print("✅ SUCCESS with OpenAI library!")
        print(f"📝 Response: {response.choices[0].message.content}")
        print(f"💰 Tokens: {response.usage.total_tokens}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED with OpenAI library: {e}")
        return False

def test_with_debug():
    """Test with debug information to see what's being sent."""
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    print("\n🔍 Testing with debug info...")
    
    try:
        # Enable debug logging
        import logging
        import httpx
        
        # Create client with debug
        client = OpenAI(
            api_key=api_key,
            http_client=httpx.Client(
                timeout=30.0,
                # Add debug logging
            )
        )
        
        print(f"🔑 Using API key: {api_key[:20]}...")
        print(f"🌐 Base URL: {client.base_url}")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello!"}],
            max_tokens=10
        )
        
        print("✅ SUCCESS with debug!")
        print(f"📝 Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED with debug: {e}")
        # Print more details about the error
        if hasattr(e, 'response'):
            print(f"🔍 Response status: {e.response.status_code if hasattr(e.response, 'status_code') else 'unknown'}")
            print(f"🔍 Response text: {e.response.text if hasattr(e.response, 'text') else 'unknown'}")
        return False

if __name__ == "__main__":
    print("🧪 Comparing curl vs OpenAI library...\n")
    
    # Test 1: Using requests (like curl)
    requests_works = test_with_requests()
    
    # Test 2: Using OpenAI library
    openai_works = test_with_openai_lib()
    
    # Test 3: Debug version
    debug_works = test_with_debug()
    
    print(f"\n📊 Results:")
    print(f"   Requests (curl-like): {'✅' if requests_works else '❌'}")
    print(f"   OpenAI library:       {'✅' if openai_works else '❌'}")
    print(f"   Debug version:        {'✅' if debug_works else '❌'}")
    
    if requests_works and not openai_works:
        print("\n💡 The issue is with the OpenAI Python library configuration!")
        print("   We can fix pdf2qa to use requests instead of the OpenAI library.")
    elif openai_works:
        print("\n🎉 OpenAI library is working now! The issue might have been temporary.")
    else:
        print("\n🤔 Both methods failed - this needs further investigation.")
