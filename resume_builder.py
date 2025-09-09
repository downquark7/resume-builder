#!/usr/bin/env python3
"""
Resume Builder Script

This script creates a tailored resume.yaml file by:
1. Reading personal data from data/ directory
2. Optionally processing job descriptions (file, URL, or keywords)
3. Using Ollama with GPT-OSS model to generate tailored resume
4. Converting JSON output to YAML format
5. Running yamlresume build to generate PDF

Usage:
    python resume_builder.py [options]

Options:
    --job-file FILE        Path to job description file
    --job-url URL          URL to fetch job description from
    --job-keywords TEXT    Keywords for job tailoring
    --model MODEL          Ollama model to use (default: gpt-oss)
    --output FILE          Output YAML file (default: resume.yaml)
    --build-pdf            Build PDF after creating YAML
    --help                 Show this help message
"""

import argparse
import json
import os
import sys
import subprocess
import requests
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
import time


class ResumeBuilder:
    def __init__(self, model: str = "gpt-oss", output_file: str = "resume.yaml"):
        self.model = model
        self.output_file = output_file
        self.data_dir = Path("data")
        self.template_file = Path("template.json")
        
    def load_personal_data(self) -> str:
        """Load all personal data from data/ directory."""
        data_content = []
        
        # Read all text files in data directory
        for file_path in self.data_dir.glob("*.txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    data_content.append(f"=== {file_path.stem.upper()} ===\n{content}\n")
        
        return "\n".join(data_content)
    
    def load_job_description(self, job_file: Optional[str] = None, 
                           job_url: Optional[str] = None, 
                           job_keywords: Optional[str] = None) -> str:
        """Load job description from file, URL, or keywords."""
        if job_file:
            with open(job_file, 'r', encoding='utf-8') as f:
                return f"JOB DESCRIPTION:\n{f.read()}\n"
        
        elif job_url:
            try:
                response = requests.get(job_url, timeout=10)
                response.raise_for_status()
                return f"JOB DESCRIPTION:\n{response.text}\n"
            except requests.RequestException as e:
                print(f"Error fetching job URL: {e}")
                return ""
        
        elif job_keywords:
            return f"JOB KEYWORDS/REQUIREMENTS:\n{job_keywords}\n"
        
        return ""
    
    def load_template(self) -> Dict[str, Any]:
        """Load the resume template structure."""
        with open(self.template_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_prompt(self, personal_data: str, job_description: str, template: Dict[str, Any], concise: bool = True) -> str:
        """Create the prompt for the LLM."""
        template_str = json.dumps(template, indent=2)
        
        prompt = f"""You are a professional resume writer. Create a tailored resume based on the following information.

PERSONAL DATA:
{personal_data}

{job_description}

TEMPLATE STRUCTURE (follow this exact JSON format):
{template_str}

INSTRUCTIONS:
{f"1. Create a CONCISE resume that matches the template structure exactly" if concise else "1. Create a DETAILED resume that matches the template structure exactly"}
2. Use the personal data provided to fill in the resume sections
3. If job description/keywords are provided, tailor the resume to highlight relevant skills and experience
{f"4. Keep it brief and focused - limit to 3-4 most relevant work experiences, 5-6 key skills with 3-4 keywords each, and 2-3 most relevant projects" if concise else "4. Include comprehensive details - 4-6 work experiences, 6-8 skills with 4-6 keywords each, and 3-4 projects"}
5. Ensure all dates are in the correct format (e.g., "Sep 1, 2016", "Jul 1, 2020")
6. Make the content professional and compelling{f" but concise" if concise else ""}
7. Use bullet points for summaries and descriptions{f" (limit to 2-3 bullets per item)" if concise else " (3-4 bullets per item)"}
8. Focus on achievements and impact, not just responsibilities
9. Include relevant keywords from the job description if provided
10. Return ONLY valid JSON that matches the template structure

Generate the resume JSON:"""

        return prompt
    
    def generate_resume_with_ollama(self, prompt: str) -> Dict[str, Any]:
        """Generate resume using Ollama with improved timeout handling."""
        try:
            print(f"Connecting to Ollama model: {self.model}")
            print("Generating resume...")
            
            # Use Ollama's HTTP API with streaming for better timeout handling
            ollama_url = "http://localhost:11434/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_ctx": 8192
                }
            }
            
            # Use a session with longer timeout
            session = requests.Session()
            session.timeout = (30, 600)  # 30s connection timeout, 10min read timeout
            
            print("Sending request to Ollama...")
            response = session.post(ollama_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result.get('response', '')
            
            if not content:
                print("Error: Empty response from Ollama")
                return None
            
            # Try to find JSON in the response with better parsing
            json_start = content.find('{')
            if json_start == -1:
                print("Error: Could not find JSON start in response")
                print(f"Response content: {content[:500]}...")
                return None
            
            # Find the matching closing brace
            brace_count = 0
            json_end = json_start
            for i, char in enumerate(content[json_start:], json_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i + 1
                        break
            
            if brace_count != 0:
                print("Error: Could not find matching closing brace in JSON")
                print(f"Response content: {content[:500]}...")
                return None
            
            json_str = content[json_start:json_end]
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                print(f"JSON string length: {len(json_str)}")
                print(f"JSON string (first 500 chars): {json_str[:500]}...")
                print(f"JSON string (last 500 chars): ...{json_str[-500:]}")
                
                # Try to save the problematic JSON for debugging
                with open("debug_resume.json", "w") as f:
                    f.write(json_str)
                print("Saved problematic JSON to debug_resume.json for inspection")
                return None
                
        except requests.exceptions.Timeout:
            print("Error: Request timed out. The model might be taking too long to respond.")
            return None
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to Ollama. Make sure Ollama is running on localhost:11434")
            return None
        except Exception as e:
            print(f"Error generating resume with Ollama: {e}")
            return None
    
    def convert_json_to_yaml(self, resume_data: Dict[str, Any]) -> str:
        """Convert JSON resume data to YAML format."""
        return yaml.dump(resume_data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def save_yaml(self, yaml_content: str) -> bool:
        """Save YAML content to file."""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            print(f"Resume saved to: {self.output_file}")
            return True
        except Exception as e:
            print(f"Error saving YAML file: {e}")
            return False
    
    def build_pdf(self) -> bool:
        """Build PDF using yamlresume."""
        try:
            print("Building PDF with yamlresume...")
            result = subprocess.run(
                ["yamlresume", "build", self.output_file],
                capture_output=True,
                text=True,
                check=True
            )
            print("PDF built successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error building PDF: {e}")
            print(f"stderr: {e.stderr}")
            return False
        except FileNotFoundError:
            print("Error: yamlresume not found. Please install it first.")
            return False
    
    def build_resume(self, job_file: Optional[str] = None,
                    job_url: Optional[str] = None,
                    job_keywords: Optional[str] = None,
                    build_pdf: bool = False,
                    concise: bool = True) -> bool:
        """Main method to build the resume."""
        print("Starting resume building process...")
        
        # Load personal data
        print("Loading personal data...")
        personal_data = self.load_personal_data()
        
        # Load job description if provided
        job_description = ""
        if job_file or job_url or job_keywords:
            print("Loading job information...")
            job_description = self.load_job_description(job_file, job_url, job_keywords)
        
        # Load template
        print("Loading template...")
        template = self.load_template()
        
        # Create prompt
        print("Creating prompt...")
        prompt = self.create_prompt(personal_data, job_description, template, concise)
        
        # Generate resume with Ollama
        resume_data = self.generate_resume_with_ollama(prompt)
        if not resume_data:
            print("Failed to generate resume")
            return False
        
        # Convert to YAML
        print("Converting to YAML...")
        yaml_content = self.convert_json_to_yaml(resume_data)
        
        # Save YAML
        if not self.save_yaml(yaml_content):
            return False
        
        # Build PDF if requested
        if build_pdf:
            return self.build_pdf()
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Build a tailored resume using Ollama and personal data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python resume_builder.py --job-file job.txt --build-pdf
  python resume_builder.py --job-url "https://example.com/job" --model gpt-oss:120b
  python resume_builder.py --job-keywords "Python, Machine Learning, Data Science"
  python resume_builder.py --detailed --build-pdf  # Detailed resume
  python resume_builder.py  # No job tailoring (concise by default)
        """
    )
    
    # Job description options (mutually exclusive)
    job_group = parser.add_mutually_exclusive_group()
    job_group.add_argument("--job-file", type=str, help="Path to job description file")
    job_group.add_argument("--job-url", type=str, help="URL to fetch job description from")
    job_group.add_argument("--job-keywords", type=str, help="Keywords for job tailoring")
    
    # Other options
    parser.add_argument("--model", type=str, default="gpt-oss", 
                       help="Ollama model to use (default: gpt-oss)")
    parser.add_argument("--output", type=str, default="resume.yaml",
                       help="Output YAML file (default: resume.yaml)")
    parser.add_argument("--build-pdf", action="store_true",
                       help="Build PDF after creating YAML")
    parser.add_argument("--concise", action="store_true", default=True,
                       help="Generate a concise resume (default: True)")
    parser.add_argument("--detailed", action="store_true",
                       help="Generate a detailed resume (overrides --concise)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.job_file and not os.path.exists(args.job_file):
        print(f"Error: Job file '{args.job_file}' not found")
        sys.exit(1)
    
    # Determine conciseness setting
    concise = args.concise and not args.detailed
    
    # Create resume builder
    builder = ResumeBuilder(model=args.model, output_file=args.output)
    
    # Build resume
    success = builder.build_resume(
        job_file=args.job_file,
        job_url=args.job_url,
        job_keywords=args.job_keywords,
        build_pdf=args.build_pdf,
        concise=concise
    )
    
    if success:
        print("Resume building completed successfully!")
    else:
        print("Resume building failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
