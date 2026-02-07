"""Test LLM configuration"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.llm import get_llm, get_embedding_model
from app.config.settings import settings

def test_llm_config():
    """Test that LLM is configured correctly"""
    print("🔧 Testing LLM Configuration...")
    print(f"API Base: {settings.openai_api_base}")
    print(f"Model: {settings.default_llm_model}")
    print(f"Temperature: {settings.llm_temperature}")
    
    llm = get_llm()
    print(f"\n✅ LLM Instance Created:")
    print(f"  - Model: {llm.model_name}")
    print(f"  - Temperature: {llm.temperature}")
    print(f"  - Max Tokens: {llm.max_tokens}")
    
    try:
        response = llm.invoke("Say 'Hello from OpenAI!' in one sentence.")
        print(f"\n✅ Test Response: {response.content}")
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_llm_config()
    sys.exit(0 if success else 1)
