#!/usr/bin/env python3
"""
Test script to verify the resume builder setup
"""

import sys
import subprocess
import os
from pathlib import Path

def test_ollama_connection():
    """Test if Ollama is running and accessible."""
    try:
        import requests
        # Test with a simple generate request
        payload = {
            "model": "gpt-oss",
            "prompt": "Hello, are you working?",
            "stream": False,
            "options": {
                "num_ctx": 8192,
                "temperature": 0.1
            }
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate", 
            json=payload, 
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        content = result.get('response', '')
        print(f"✓ Ollama connection successful. Model responded: {content[:50]}...")
        return True
    except requests.exceptions.ConnectionError:
        print("✗ Ollama connection failed: Could not connect to localhost:11434. Make sure Ollama is running.")
        return False
    except Exception as e:
        print(f"✗ Ollama connection failed: {e}")
        return False

def test_yamlresume():
    """Test if yamlresume is installed."""
    try:
        result = subprocess.run(["yamlresume", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ yamlresume is installed: {result.stdout.strip()}")
            return True
        else:
            print("✗ yamlresume not found or not working")
            return False
    except FileNotFoundError:
        print("✗ yamlresume not found. Install with: npm install -g yamlresume")
        return False

def test_data_files():
    """Test if data files exist."""
    data_dir = Path("data")
    if not data_dir.exists():
        print("✗ data/ directory not found")
        return False
    
    txt_files = list(data_dir.glob("*.txt"))
    if not txt_files:
        print("✗ No .txt files found in data/ directory")
        return False
    
    print(f"✓ Found {len(txt_files)} data files: {[f.name for f in txt_files]}")
    return True

def test_template():
    """Test if template.json exists."""
    template_file = Path("template.json")
    if not template_file.exists():
        print("✗ template.json not found")
        return False
    
    try:
        import json
        with open(template_file, 'r') as f:
            json.load(f)
        print("✓ template.json is valid JSON")
        return True
    except Exception as e:
        print(f"✗ template.json is invalid: {e}")
        return False

def main():
    print("Testing resume builder setup...\n")
    
    tests = [
        ("Data files", test_data_files),
        ("Template", test_template),
        ("Ollama connection", test_ollama_connection),
        ("yamlresume", test_yamlresume),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        if not test_func():
            all_passed = False
        print()
    
    if all_passed:
        print("✓ All tests passed! Setup is ready.")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
