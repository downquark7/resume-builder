#!/usr/bin/env python3
"""
Example usage of the Resume Generator.

This script demonstrates how to use the ResumeGenerator class programmatically
without the command line interface.
"""

import sys
from resume_generator import ResumeGenerator

def example_generic_resume():
    """Example: Generate a generic resume."""
    print("Example 1: Generic Resume")
    print("-" * 30)
    
    generator = ResumeGenerator(slow_mode=False)
    
    try:
        # This would normally call the LLM, but we'll just show the setup
        data_content = generator.load_data_files()
        prompt = generator.create_prompt(data_content)
        
        print(f"✓ Data loaded: {len(data_content)} characters")
        print(f"✓ Prompt created: {len(prompt)} characters")
        print("✓ Ready to call LLM (requires Ollama running)")
        
    except Exception as e:
        print(f"✗ Error: {e}")

def example_keyword_tailoring():
    """Example: Generate resume tailored to keywords."""
    print("\nExample 2: Keyword Tailoring")
    print("-" * 30)
    
    generator = ResumeGenerator(slow_mode=False)
    keywords = "Python, Machine Learning, AWS, Docker, Kubernetes"
    
    try:
        data_content = generator.load_data_files()
        tailoring_info = f"Tailor this resume to highlight these keywords and skills: {keywords}"
        prompt = generator.create_prompt(data_content, tailoring_info)
        
        print(f"✓ Keywords: {keywords}")
        print(f"✓ Data loaded: {len(data_content)} characters")
        print(f"✓ Tailored prompt created: {len(prompt)} characters")
        print("✓ Ready to call LLM (requires Ollama running)")
        
    except Exception as e:
        print(f"✗ Error: {e}")

def example_job_file_tailoring():
    """Example: Generate resume tailored to job file."""
    print("\nExample 3: Job File Tailoring")
    print("-" * 30)
    
    generator = ResumeGenerator(slow_mode=False)
    job_file = "sample_job.txt"
    
    try:
        # Load job description
        with open(job_file, 'r') as f:
            job_description = f.read()
        
        data_content = generator.load_data_files()
        tailoring_info = f"Tailor this resume for the following job posting:\n{job_description}"
        prompt = generator.create_prompt(data_content, tailoring_info)
        
        print(f"✓ Job file: {job_file}")
        print(f"✓ Job description length: {len(job_description)} characters")
        print(f"✓ Data loaded: {len(data_content)} characters")
        print(f"✓ Tailored prompt created: {len(prompt)} characters")
        print("✓ Ready to call LLM (requires Ollama running)")
        
    except Exception as e:
        print(f"✗ Error: {e}")

def example_slow_mode():
    """Example: Using slow mode with more powerful model."""
    print("\nExample 4: Slow Mode (More Powerful Model)")
    print("-" * 30)
    
    generator = ResumeGenerator(slow_mode=True)
    
    try:
        data_content = generator.load_data_files()
        prompt = generator.create_prompt(data_content)
        
        print(f"✓ Model: {generator.model}")
        print(f"✓ Context size: {generator.context_size}")
        print(f"✓ Data loaded: {len(data_content)} characters")
        print(f"✓ Prompt created: {len(prompt)} characters")
        print("✓ Ready to call LLM (requires Ollama running)")
        
    except Exception as e:
        print(f"✗ Error: {e}")

def show_available_commands():
    """Show available command line examples."""
    print("\nCommand Line Examples:")
    print("-" * 30)
    
    commands = [
        "# Generic resume",
        "python3 resume_generator.py",
        "",
        "# Tailored to keywords",
        "python3 resume_generator.py --keywords 'Python, Machine Learning, AWS'",
        "",
        "# Tailored to job file",
        "python3 resume_generator.py --job-file sample_job.txt",
        "",
        "# Tailored to job URL",
        "python3 resume_generator.py --job-url 'https://example.com/job'",
        "",
        "# Using slow mode (more powerful model)",
        "python3 resume_generator.py --slow --keywords 'React, Node.js'",
        "",
        "# Get help",
        "python3 resume_generator.py --help"
    ]
    
    for cmd in commands:
        print(cmd)

def main():
    """Run all examples."""
    print("Resume Generator - Usage Examples")
    print("=" * 50)
    
    example_generic_resume()
    example_keyword_tailoring()
    example_job_file_tailoring()
    example_slow_mode()
    show_available_commands()
    
    print("\n" + "=" * 50)
    print("Note: To actually generate resumes, ensure Ollama is running with:")
    print("  ollama serve")
    print("  ollama pull gpt-oss")
    print("  ollama pull gpt-oss:120b  # Optional, for --slow mode")

if __name__ == "__main__":
    main()