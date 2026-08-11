import asyncio
import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.ai.factory import AIFactory
from app.ai.schemas import AIRequest, Message, Role

async def test_providers():
    print("Testing Providers Endpoint Logic...")
    from app.api.v1.endpoints.providers import get_providers
    status = await get_providers()
    for s in status:
        print(f"Provider: {s['name']} - Available: {s['available']} - Health: {s['health_status']}")
        
    print("\nTesting Provider Generation (with mock keys)...")
    
    # We will test factory initialization and expected behavior
    # For actual API calls, we would need real keys. We'll test with dummy keys to see if they fail correctly.
    
    request = AIRequest(
        model="gpt-4o",
        messages=[Message(role=Role.user, content="Say 'test'")],
        temperature=0.0,
        max_tokens=10
    )
    
    try:
        p = AIFactory.get_provider("openai", api_key="sk-dummy")
        # Should raise AIProviderException or RateLimit due to dummy key (usually 401 Unauthorized)
        res = await p.run(request)
        print(f"OpenAI Success (unexpected with dummy key): {res}")
    except Exception as e:
        print(f"OpenAI correctly failed with dummy key: {type(e).__name__} - {str(e)}")

    request.model = "gemini-1.5-pro"
    try:
        p = AIFactory.get_provider("gemini", api_key="dummy_key")
        res = await p.run(request)
        print(f"Gemini Success: {res}")
    except Exception as e:
        print(f"Gemini correctly failed with dummy key: {type(e).__name__} - {str(e)}")
        
    request.model = "llama3-8b-8192"
    try:
        p = AIFactory.get_provider("groq", api_key="gsk_dummy")
        res = await p.run(request)
        print(f"Groq Success: {res}")
    except Exception as e:
        print(f"Groq correctly failed with dummy key: {type(e).__name__} - {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_providers())
