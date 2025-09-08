#!/bin/bash
# Setup script for Resume Generator

echo "Resume Generator Setup"
echo "====================="

# Check if Python 3.13 is available
echo "Checking Python version..."
python3 --version

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt --break-system-packages

# Check if Ollama is installed
echo "Checking for Ollama..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo "✓ Ollama is running"
        
        # Check for required models
        echo "Checking for required models..."
        if ollama list | grep -q "gpt-oss"; then
            echo "✓ gpt-oss model found"
        else
            echo "Installing gpt-oss model..."
            ollama pull gpt-oss
        fi
        
        if ollama list | grep -q "gpt-oss:120b"; then
            echo "✓ gpt-oss:120b model found"
        else
            echo "Installing gpt-oss:120b model (optional, for --slow mode)..."
            ollama pull gpt-oss:120b
        fi
    else
        echo "⚠ Ollama is not running. Please start it with: ollama serve"
    fi
else
    echo "⚠ Ollama is not installed. Please install it from https://ollama.ai/"
fi

# Check if yamlresume-cli is installed
echo "Checking for yamlresume-cli..."
if command -v yamlresume &> /dev/null; then
    echo "✓ yamlresume-cli is installed"
else
    echo "⚠ yamlresume-cli is not installed. Please install it with: npm install -g yamlresume-cli"
fi

# Check data directory
echo "Checking data directory..."
if [ -d "./data" ]; then
    echo "✓ Data directory exists"
    echo "Data files found:"
    ls -la ./data/*.txt 2>/dev/null || echo "  No .txt files found in ./data/"
else
    echo "Creating data directory..."
    mkdir -p ./data
    echo "✓ Data directory created"
fi

# Test the script
echo "Testing resume generator..."
python3 test_resume_generator.py

echo ""
echo "Setup complete!"
echo ""
echo "To generate a resume, run:"
echo "  python3 resume_generator.py --help"
echo ""
echo "Example commands:"
echo "  python3 resume_generator.py                                    # Generic resume"
echo "  python3 resume_generator.py --keywords 'Python, ML, AWS'      # Tailored to keywords"
echo "  python3 resume_generator.py --job-file sample_job.txt         # Tailored to job file"
echo "  python3 resume_generator.py --slow --keywords 'React, Node'   # Using slow mode"