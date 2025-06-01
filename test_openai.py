#!/usr/bin/env python3
"""
Simple test script to check OpenAI API connectivity and quota.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

def test_openai_api():
    """Test OpenAI API with a minimal request."""
    
    # Load environment variables (override existing ones)
    load_dotenv(override=True)
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    
    # Initialize OpenAI client
    try:
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized")

        # Try to get organization info
        try:
            # This might help identify which org the key belongs to
            models = client.models.list()
            print(f"✅ Can access models list (found {len(models.data)} models)")
        except Exception as e:
            print(f"⚠️  Cannot list models: {e}")

    except Exception as e:
        print(f"❌ ERROR initializing OpenAI client: {e}")
        return False
    
    # Test with a very simple, low-cost request
    try:
        print("\n🔄 Testing API with minimal request...")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello'"}
            ],
            max_tokens=5,  # Very small to minimize cost
            temperature=0
        )

        print("✅ SUCCESS! OpenAI API is working")
        print(f"📝 Response: {response.choices[0].message.content}")
        print(f"💰 Tokens used: {response.usage.total_tokens}")
        return True

    except Exception as e:
        print(f"❌ ERROR calling OpenAI API: {e}")

        # Get more detailed error information
        error_str = str(e)
        print(f"\n🔍 Full error details: {error_str}")

        # Check if it's a quota error specifically
        if "quota" in error_str.lower() or "429" in error_str:
            print("\n💡 Possible causes for quota error with valid billing:")
            print("   1. API key might be from a different organization")
            print("   2. Rate limiting (too many requests recently)")
            print("   3. Model-specific quota limits")
            print("   4. Temporary OpenAI service issue")
            print("\n🔧 Try these solutions:")
            print("   1. Wait 1-2 minutes and try again")
            print("   2. Check if API key belongs to correct organization")
            print("   3. Try a different model (gpt-4o-mini)")

        return False

def test_alternative_model(client):
    """Test with a different model to see if it's model-specific."""
    try:
        print("\n🔄 Testing with gpt-4o-mini model...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say 'Hi'"}
            ],
            max_tokens=3,
            temperature=0
        )

        print("✅ SUCCESS with gpt-4o-mini!")
        print(f"📝 Response: {response.choices[0].message.content}")
        return True

    except Exception as e:
        print(f"❌ gpt-4o-mini also failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing OpenAI API connectivity...\n")
    success = test_openai_api()

    if not success:
        # Try alternative model
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            alt_success = test_alternative_model(client)
            if alt_success:
                print("\n💡 gpt-4o-mini works! Consider switching pdf2qa to use this model.")
                success = True
        except:
            pass

    if success:
        print("\n🎉 Your OpenAI API is ready for pdf2qa!")
    else:
        print("\n⚠️  Fix the API issue above, then try running pdf2qa again")
