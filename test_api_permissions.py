#!/usr/bin/env python3
"""
Test what permissions and access the OpenAI API key has.
"""

import os
import requests
from dotenv import load_dotenv

def test_api_endpoints():
    """Test various OpenAI API endpoints to see what's accessible."""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        return
    
    print(f"🔑 Testing API key: {api_key[:20]}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test different endpoints
    endpoints = [
        {
            "name": "Models List",
            "url": "https://api.openai.com/v1/models",
            "method": "GET"
        },
        {
            "name": "Account Info",
            "url": "https://api.openai.com/v1/dashboard/billing/subscription",
            "method": "GET"
        },
        {
            "name": "Usage Info",
            "url": "https://api.openai.com/v1/dashboard/billing/usage",
            "method": "GET"
        },
        {
            "name": "Credit Grants",
            "url": "https://api.openai.com/v1/dashboard/billing/credit_grants",
            "method": "GET"
        },
        {
            "name": "Chat Completion (minimal)",
            "url": "https://api.openai.com/v1/chat/completions",
            "method": "POST",
            "data": {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 1
            }
        }
    ]
    
    print("\n🧪 Testing API endpoints...\n")
    
    for endpoint in endpoints:
        try:
            print(f"🔄 Testing {endpoint['name']}...")
            
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], headers=headers, timeout=10)
            else:
                response = requests.post(endpoint['url'], headers=headers, json=endpoint['data'], timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint['name']}: SUCCESS")
                
                # Show some response details for successful calls
                if endpoint['name'] == 'Models List':
                    data = response.json()
                    print(f"   📊 Found {len(data.get('data', []))} models")
                elif endpoint['name'] == 'Chat Completion (minimal)':
                    data = response.json()
                    usage = data.get('usage', {})
                    print(f"   💰 Tokens used: {usage.get('total_tokens', 'unknown')}")
                    
            else:
                print(f"❌ {endpoint['name']}: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    error_type = error_data.get('error', {}).get('type', 'unknown')
                    print(f"   🔍 Error: {error_type} - {error_msg}")
                except:
                    print(f"   🔍 Raw response: {response.text[:200]}")
                    
        except requests.exceptions.Timeout:
            print(f"⏰ {endpoint['name']}: TIMEOUT")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint['name']}: REQUEST ERROR - {e}")
        except Exception as e:
            print(f"❌ {endpoint['name']}: UNEXPECTED ERROR - {e}")
        
        print()  # Empty line for readability

if __name__ == "__main__":
    print("🔍 Testing OpenAI API key permissions and access...\n")
    test_api_endpoints()
