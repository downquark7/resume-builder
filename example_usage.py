#!/usr/bin/env python3
"""
Example usage of the GPT-OSS client with 8k context size handling.
"""

from gpt_oss_client import GPTOSSClient, GPTOSSConfig
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def example_basic_usage():
    """Basic usage example."""
    print("=== Basic Usage Example ===")
    
    # Configure the client
    config = GPTOSSConfig(
        base_url="http://localhost:8000",  # Adjust to your local server
        max_context_size=8192,
        temperature=0.7,
        max_tokens=1024
    )
    
    client = GPTOSSClient(config)
    
    # Test connection
    if not client.test_connection():
        print("❌ Failed to connect to GPT-OSS model")
        print("Make sure your local server is running on http://localhost:8000")
        return
    
    print("✅ Connected to GPT-OSS model")
    
    # Simple conversation
    messages = [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a simple Python function to calculate fibonacci numbers."}
    ]
    
    try:
        response = client.generate_response(messages)
        content = response["choices"][0]["message"]["content"]
        print(f"Assistant: {content}")
    except Exception as e:
        print(f"Error: {e}")

def example_context_handling():
    """Example showing 8k context size handling."""
    print("\n=== Context Size Handling Example ===")
    
    config = GPTOSSConfig(max_context_size=8192)
    client = GPTOSSClient(config)
    
    # Create a conversation that might exceed context size
    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes long texts."},
        {"role": "user", "content": "Please summarize this very long text: " + "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 200}  # Very long text
    ]
    
    print(f"Original message count: {len(messages)}")
    print(f"Estimated context size: {sum(len(msg['content']) for msg in messages) // 4} tokens")
    
    try:
        response = client.generate_response(messages)
        content = response["choices"][0]["message"]["content"]
        print(f"Assistant: {content}")
    except Exception as e:
        print(f"Error: {e}")

def example_streaming():
    """Example of streaming responses."""
    print("\n=== Streaming Example ===")
    
    config = GPTOSSConfig(max_context_size=8192)
    client = GPTOSSClient(config)
    
    messages = [
        {"role": "system", "content": "You are a creative writing assistant."},
        {"role": "user", "content": "Write a short story about a robot learning to paint."}
    ]
    
    try:
        print("Streaming response:")
        response = client.generate_response(messages, stream=True)
        content = response["choices"][0]["message"]["content"]
        print(f"Assistant: {content}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all examples."""
    print("GPT-OSS Client Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_usage()
    example_context_handling()
    example_streaming()
    
    print("\n" + "=" * 50)
    print("Examples completed!")

if __name__ == "__main__":
    main()