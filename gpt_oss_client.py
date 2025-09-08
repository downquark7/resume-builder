#!/usr/bin/env python3
"""
GPT-OSS Model Client
Connects to a locally hosted GPT-OSS model with 8k context size support.
"""

import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GPTOSSConfig:
    """Configuration for GPT-OSS model connection."""
    base_url: str = "http://localhost:8000"  # Default local server
    api_key: Optional[str] = None
    max_context_size: int = 8192  # 8k context size
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30

class GPTOSSClient:
    """Client for connecting to locally hosted GPT-OSS model."""
    
    def __init__(self, config: GPTOSSConfig):
        self.config = config
        self.session = requests.Session()
        
        # Set up headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "GPT-OSS-Python-Client/1.0"
        })
        
        if self.config.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.config.api_key}"
            })
    
    def _validate_context_size(self, messages: List[Dict[str, str]]) -> bool:
        """Validate that the total context size doesn't exceed 8k tokens."""
        # Simple token estimation (rough approximation: 1 token ≈ 4 characters)
        total_chars = sum(len(msg["content"]) for msg in messages)
        estimated_tokens = total_chars // 4
        
        if estimated_tokens > self.config.max_context_size:
            logger.warning(f"Context size ({estimated_tokens} tokens) exceeds limit ({self.config.max_context_size})")
            return False
        return True
    
    def _truncate_context(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Truncate messages to fit within 8k context size."""
        # Simple truncation strategy: keep system message and recent messages
        if not messages:
            return messages
            
        # Find system message
        system_msg = None
        other_msgs = []
        
        for msg in messages:
            if msg.get("role") == "system":
                system_msg = msg
            else:
                other_msgs.append(msg)
        
        # Calculate available space for non-system messages
        system_chars = len(system_msg["content"]) if system_msg else 0
        available_chars = (self.config.max_context_size * 4) - system_chars - 1000  # 1000 char buffer
        
        # Keep recent messages that fit
        truncated_msgs = []
        current_chars = 0
        
        for msg in reversed(other_msgs):
            msg_chars = len(msg["content"])
            if current_chars + msg_chars <= available_chars:
                truncated_msgs.insert(0, msg)
                current_chars += msg_chars
            else:
                break
        
        # Reconstruct messages list
        result = []
        if system_msg:
            result.append(system_msg)
        result.extend(truncated_msgs)
        
        return result
    
    def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a response from the GPT-OSS model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            stream: Whether to stream the response
            
        Returns:
            Dictionary containing the response data
        """
        # Validate and truncate context if needed
        if not self._validate_context_size(messages):
            messages = self._truncate_context(messages)
            logger.info("Context truncated to fit within 8k limit")
        
        # Prepare the request payload
        payload = {
            "model": "gpt-oss",  # Adjust model name as needed
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": stream
        }
        
        try:
            # Make the request
            response = self.session.post(
                f"{self.config.base_url}/v1/chat/completions",
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream_response(response)
            else:
                return response.json()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response: {e}")
            raise
    
    def _handle_stream_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle streaming response from the model."""
        # This is a simplified implementation
        # In a real scenario, you'd want to handle streaming properly
        full_content = ""
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # Remove 'data: ' prefix
                    if data_str.strip() == '[DONE]':
                        break
                    try:
                        data = json.loads(data_str)
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                full_content += delta['content']
                    except json.JSONDecodeError:
                        continue
        
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": full_content
                },
                "finish_reason": "stop"
            }]
        }
    
    def test_connection(self) -> bool:
        """Test the connection to the GPT-OSS model."""
        try:
            response = self.session.get(f"{self.config.base_url}/health")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

def main():
    """Example usage of the GPT-OSS client."""
    # Configuration
    config = GPTOSSConfig(
        base_url="http://localhost:8000",  # Adjust as needed
        max_context_size=8192
    )
    
    # Create client
    client = GPTOSSClient(config)
    
    # Test connection
    if not client.test_connection():
        logger.error("Failed to connect to GPT-OSS model. Is it running?")
        return
    
    logger.info("Successfully connected to GPT-OSS model")
    
    # Example conversation
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Hello! Can you help me understand how to use this GPT-OSS model?"}
    ]
    
    try:
        response = client.generate_response(messages)
        
        if "choices" in response and len(response["choices"]) > 0:
            content = response["choices"][0]["message"]["content"]
            print(f"Assistant: {content}")
        else:
            print("No response received")
            
    except Exception as e:
        logger.error(f"Error generating response: {e}")

if __name__ == "__main__":
    main()