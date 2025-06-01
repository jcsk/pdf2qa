#!/usr/bin/env python3
"""
Test different OpenAI models to see if quota is model-specific.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

def test_models():
    """Test different models to see which ones work."""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        return
    
    print(f"🔑 Testing API key: {api_key[:20]}...")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Models to test
    models_to_test = [
        "gpt-3.5-turbo",
        "gpt-4o-mini", 
        "gpt-4o",
        "gpt-4",
        "text-davinci-003"  # Legacy model
    ]
    
    print("\n🧪 Testing different models...\n")
    
    for model in models_to_test:
        try:
            print(f"🔄 Testing {model}...")
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": "Say 'OK'"}
                ],
                max_tokens=1,
                temperature=0
            )
            
            print(f"✅ {model}: SUCCESS!")
            print(f"   📝 Response: {response.choices[0].message.content}")
            print(f"   💰 Tokens: {response.usage.total_tokens}")
            return True  # If any model works, we're good
            
        except Exception as e:
            error_str = str(e)
            if "quota" in error_str.lower() or "429" in error_str:
                print(f"❌ {model}: QUOTA ERROR")
            elif "model" in error_str.lower() and "not found" in error_str.lower():
                print(f"⚠️  {model}: MODEL NOT AVAILABLE")
            else:
                print(f"❌ {model}: {error_str}")
        
        print()
    
    print("❌ No models worked - this appears to be an account-level quota issue")
    return False

if __name__ == "__main__":
    print("🔍 Testing different OpenAI models...\n")
    success = test_models()
    
    if not success:
        print("\n💡 Recommendations:")
        print("   1. Check your OpenAI usage dashboard")
        print("   2. Verify you're in the correct organization")
        print("   3. Contact OpenAI support")
        print("   4. Meanwhile, use pdf2qa with --skip-extract --skip-qa")
