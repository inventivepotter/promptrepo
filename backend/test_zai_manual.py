"""
Manual test script for ZAI provider using the unified AnyLLM interface.
Replace YOUR_ZAI_API_KEY with your actual API key and run this script.

Usage:
    cd backend
    uv run python test_zai_manual.py
"""
import asyncio
from typing import cast, Any
from lib.any_llm.any_llm_adapter import acompletion, alist_models
from any_llm.types.completion import ChatCompletion, ChatCompletionChunk


async def test_zai_completion():
    """Test ZAI completion using unified AnyLLM interface."""
    print("=" * 60)
    print("Testing ZAI Completion")
    print("=" * 60)
    
    # REPLACE THIS with your actual ZAI API key
    api_key = "d69f1ff7c5b6435e8c71f68c2ba2bfa0.omRv5dMdNzpkqhAL"
    api_base = "https://api.z.ai/api/coding/paas/v4"
    
    # Test messages
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! Tell me a short joke about programming."}
    ]
    
    try:
        # Non-streaming completion
        print("\n1. Testing non-streaming completion...")
        completion_result = await acompletion(
            model="zai/glm-4.6",
            messages=messages,
            api_key=api_key,
            api_base=api_base,
            temperature=0.7,
            max_tokens=150
        )
        
        response = cast(ChatCompletion, completion_result)
        print(f"\nResponse ID: {response.id}")
        print(f"Model: {response.model}")
        print(f"Content: {response.choices[0].message.content}")
        print(f"Finish Reason: {response.choices[0].finish_reason}")
        
        if response.usage:
            print(f"\nUsage:")
            print(f"  Prompt tokens: {response.usage.prompt_tokens}")
            print(f"  Completion tokens: {response.usage.completion_tokens}")
            print(f"  Total tokens: {response.usage.total_tokens}")
        
        print("\n✅ Non-streaming completion successful!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    # Streaming completion
    try:
        print("\n" + "=" * 60)
        print("2. Testing streaming completion...")
        print("-" * 60)
        
        stream_result = await acompletion(
            model="zai/glm-4.6",
            messages=messages,
            api_key=api_key,
            api_base=api_base,
            temperature=0.7,
            max_tokens=150,
            stream=True
        )
        
        print("Streaming response: ", end="", flush=True)
        async for chunk in stream_result:  # type: ignore
            chunk_typed = cast(ChatCompletionChunk, chunk)
            if chunk_typed.choices and len(chunk_typed.choices) > 0:
                delta = chunk_typed.choices[0].delta
                if delta.content:
                    print(delta.content, end="", flush=True)
        
        print("\n\n✅ Streaming completion successful!")
        
    except Exception as e:
        print(f"\n❌ Streaming error: {e}")
        return False
    
    return True


async def test_zai_list_models():
    """Test listing ZAI models using unified AnyLLM interface."""
    print("\n" + "=" * 60)
    print("Testing ZAI List Models")
    print("=" * 60)
    
    # REPLACE THIS with your actual ZAI API key
    api_key = "YOUR_ZAI_API_KEY"
    api_base = "https://api.z.ai/api/coding/paas/v4"
    
    try:
        models = await alist_models(
            provider="zai",
            api_key=api_key,
            api_base=api_base
        )
        
        print(f"\nAvailable models: {len(models)}")
        for model in models:
            print(f"  - {model.id}")
        
        print("\n✅ List models successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error listing models: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("ZAI Provider Test Suite (Unified AnyLLM Interface)")
    print("=" * 60)
    print("\nThis tests that ZAI provider works through the unified")
    print("AnyLLM interface without special if-conditions.\n")
    
    # Test completion
    completion_success = await test_zai_completion()
    
    # Test list models
    models_success = await test_zai_list_models()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Completion test: {'✅ PASSED' if completion_success else '❌ FAILED'}")
    print(f"List models test: {'✅ PASSED' if models_success else '❌ FAILED'}")
    
    if completion_success and models_success:
        print("\n🎉 All tests passed! ZAI provider is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())