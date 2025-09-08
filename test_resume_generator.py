#!/usr/bin/env python3
"""
Test script for resume generator functionality.
This script tests the data loading and template functionality without requiring Ollama.
"""

import json
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, '.')

from resume_generator import ResumeGenerator

def test_data_loading():
    """Test the data loading functionality."""
    print("Testing data loading...")
    
    generator = ResumeGenerator()
    data_content = generator.load_data_files()
    
    print(f"Loaded data content length: {len(data_content)} characters")
    print("First 500 characters of loaded data:")
    print("-" * 50)
    print(data_content[:500])
    print("-" * 50)
    
    return data_content

def test_template_loading():
    """Test the template loading functionality."""
    print("\nTesting template loading...")
    
    generator = ResumeGenerator()
    template = generator.template
    
    print(f"Template loaded successfully")
    print(f"Template has {len(template)} top-level keys: {list(template.keys())}")
    
    if 'content' in template:
        content = template['content']
        print(f"Content section has {len(content)} sections: {list(content.keys())}")
    
    return template

def test_prompt_creation():
    """Test the prompt creation functionality."""
    print("\nTesting prompt creation...")
    
    generator = ResumeGenerator()
    data_content = generator.load_data_files()
    
    # Test different tailoring scenarios
    scenarios = [
        ("Generic", ""),
        ("Keywords", "Python, Machine Learning, AWS"),
        ("Job File", "Tailor this resume for a software engineering position...")
    ]
    
    for scenario_name, tailoring_info in scenarios:
        prompt = generator.create_prompt(data_content, tailoring_info)
        print(f"\n{scenario_name} prompt length: {len(prompt)} characters")
        print(f"First 200 characters:")
        print("-" * 30)
        print(prompt[:200])
        print("-" * 30)

def test_file_structure():
    """Test the expected file structure."""
    print("\nTesting file structure...")
    
    required_files = [
        'template.json',
        'resume_generator.py',
        'requirements.txt',
        'README.md'
    ]
    
    data_dir = Path('./data')
    data_files = list(data_dir.glob('*.txt')) if data_dir.exists() else []
    
    print("Required files:")
    for file in required_files:
        exists = Path(file).exists()
        print(f"  {file}: {'✓' if exists else '✗'}")
    
    print(f"\nData files found: {len(data_files)}")
    for file in data_files:
        print(f"  {file.name}")

def main():
    """Run all tests."""
    print("Resume Generator Test Suite")
    print("=" * 40)
    
    try:
        test_file_structure()
        test_template_loading()
        test_data_loading()
        test_prompt_creation()
        
        print("\n" + "=" * 40)
        print("All tests completed successfully!")
        print("\nTo run the actual resume generation, ensure Ollama is running and use:")
        print("  python3 resume_generator.py --keywords 'Python, Machine Learning'")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()