# GPT-OSS Python Client

A Python client for connecting to locally hosted GPT-OSS models with 8k context size support.

## Features

- ✅ Connect to locally hosted GPT-OSS models
- ✅ 8k context size handling with automatic truncation
- ✅ Streaming response support
- ✅ Error handling and logging
- ✅ Configurable parameters
- ✅ Python 3.13 compatible

## Installation

1. Install Python 3.13
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from gpt_oss_client import GPTOSSClient, GPTOSSConfig

# Configure the client
config = GPTOSSConfig(
    base_url="http://localhost:8000",  # Your local server URL
    max_context_size=8192,             # 8k context size
    temperature=0.7,
    max_tokens=1024
)

# Create client
client = GPTOSSClient(config)

# Test connection
if client.test_connection():
    print("Connected successfully!")
else:
    print("Connection failed!")

# Generate response
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
]

response = client.generate_response(messages)
print(response["choices"][0]["message"]["content"])
```

### Running Examples

```bash
python example_usage.py
```

## Configuration

The `GPTOSSConfig` class supports the following parameters:

- `base_url`: URL of your local GPT-OSS server (default: "http://localhost:8000")
- `api_key`: API key if required (default: None)
- `max_context_size`: Maximum context size in tokens (default: 8192)
- `temperature`: Response temperature (default: 0.7)
- `max_tokens`: Maximum tokens to generate (default: 2048)
- `timeout`: Request timeout in seconds (default: 30)

## Context Size Handling

The client automatically handles 8k context size limits by:

1. **Validation**: Checking if the total context exceeds 8k tokens
2. **Truncation**: Automatically truncating messages to fit within limits
3. **Preservation**: Keeping system messages and recent user messages

## Error Handling

The client includes comprehensive error handling for:

- Connection failures
- Invalid responses
- Context size violations
- Network timeouts

## Requirements

- Python 3.13+
- Local GPT-OSS model server running
- Dependencies listed in `requirements.txt`

## Notes

- The client assumes your local GPT-OSS server follows the OpenAI API format
- Adjust the `base_url` and model name as needed for your setup
- Context size estimation uses a rough approximation (1 token ≈ 4 characters)