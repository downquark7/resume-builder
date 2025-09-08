#!/usr/bin/env python3
"""
Resume Generator Script

This script generates tailored resumes using a locally hosted Ollama model.
It supports various tailoring options and outputs resumes in PDF format.
"""

import argparse
import json
import logging
import os
import requests
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import sys


class ResumeGenerator:
    def __init__(self, slow_mode: bool = False):
        """Initialize the resume generator.
        
        Args:
            slow_mode: If True, use gpt-oss:120b model, otherwise use gpt-oss
        """
        self.slow_mode = slow_mode
        self.model = "gpt-oss:120b" if slow_mode else "gpt-oss"
        self.ollama_url = "http://localhost:11434/api/generate"
        self.context_size = 8000
        
        # Set up logging
        self.setup_logging()
        
        # Load template
        self.template = self.load_template()
        
    def setup_logging(self):
        """Set up logging for debugging LLM inputs and outputs."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('resume_generation.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_template(self) -> Dict[str, Any]:
        """Load the resume template from template.json."""
        try:
            with open('template.json', 'r') as f:
                template = json.load(f)
            self.logger.info("Successfully loaded resume template")
            return template
        except FileNotFoundError:
            self.logger.error("template.json not found")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in template.json: {e}")
            raise
            
    def load_data_files(self) -> str:
        """Load all text files from the ./data directory."""
        data_dir = Path('./data')
        if not data_dir.exists():
            self.logger.warning("Data directory not found, creating empty directory")
            data_dir.mkdir(exist_ok=True)
            return ""
            
        data_content = []
        for file_path in data_dir.glob('*.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        data_content.append(f"=== {file_path.name} ===\n{content}")
            except Exception as e:
                self.logger.warning(f"Could not read {file_path}: {e}")
                
        combined_data = "\n\n".join(data_content)
        self.logger.info(f"Loaded data from {len(data_content)} files")
        return combined_data
        
    def fetch_job_description(self, job_url: str) -> str:
        """Fetch job description from URL."""
        try:
            response = requests.get(job_url, timeout=30)
            response.raise_for_status()
            # Simple text extraction - in production, you might want to use BeautifulSoup
            content = response.text
            self.logger.info(f"Successfully fetched job description from {job_url}")
            return content
        except Exception as e:
            self.logger.error(f"Failed to fetch job description from {job_url}: {e}")
            raise
            
    def load_job_file(self, job_file: str) -> str:
        """Load job description from file."""
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                content = f.read()
            self.logger.info(f"Successfully loaded job description from {job_file}")
            return content
        except Exception as e:
            self.logger.error(f"Failed to load job file {job_file}: {e}")
            raise
            
    def create_prompt(self, data_content: str, tailoring_info: str = "") -> str:
        """Create the prompt for the LLM."""
        prompt = f"""You are a professional resume writer. I need you to create a tailored resume in JSON format based on the following information:

RESUME TEMPLATE STRUCTURE:
{json.dumps(self.template, indent=2)}

PERSONAL DATA TO USE:
{data_content}

TAILORING INFORMATION:
{tailoring_info if tailoring_info else "Create a generic resume using the personal data provided."}

INSTRUCTIONS:
1. Use the exact JSON structure from the template above
2. Fill in all fields with relevant information from the personal data
3. Tailor the content based on the tailoring information provided
4. Ensure all dates, names, and details are realistic and consistent
5. Make the resume professional and compelling
6. Return ONLY the JSON object, no additional text or formatting
7. Ensure the JSON is valid and complete

Generate the tailored resume now:"""

        return prompt
        
    def call_ollama(self, prompt: str) -> str:
        """Call the Ollama model with the given prompt."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": self.context_size,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        self.logger.info(f"Calling Ollama model: {self.model}")
        self.logger.info(f"Prompt length: {len(prompt)} characters")
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get('response', '')
            
            self.logger.info(f"Received response from Ollama (length: {len(generated_text)} characters)")
            self.logger.debug(f"Ollama response: {generated_text}")
            
            return generated_text
            
        except Exception as e:
            self.logger.error(f"Failed to call Ollama: {e}")
            raise
            
    def parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response and extract JSON."""
        try:
            # Try to find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
                
            json_str = response[start_idx:end_idx]
            resume_data = json.loads(json_str)
            
            self.logger.info("Successfully parsed JSON from LLM response")
            return resume_data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON from LLM response: {e}")
            self.logger.error(f"Response content: {response}")
            raise
        except Exception as e:
            self.logger.error(f"Error parsing LLM response: {e}")
            raise
            
    def save_json_resume(self, resume_data: Dict[str, Any], filename: str = "generated_resume.json"):
        """Save the resume data as JSON."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Saved JSON resume to {filename}")
        
    def convert_to_yaml(self, resume_data: Dict[str, Any], filename: str = "generated_resume.yaml"):
        """Convert resume data to YAML format."""
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(resume_data, f, default_flow_style=False, allow_unicode=True)
        self.logger.info(f"Converted and saved YAML resume to {filename}")
        return filename
        
    def build_pdf(self, yaml_file: str):
        """Build PDF from YAML file using yamlresume."""
        try:
            cmd = ["yamlresume", "build", yaml_file]
            self.logger.info(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.logger.info("Successfully generated PDF resume")
                self.logger.info(f"yamlresume output: {result.stdout}")
            else:
                self.logger.error(f"yamlresume failed with return code {result.returncode}")
                self.logger.error(f"Error output: {result.stderr}")
                raise subprocess.CalledProcessError(result.returncode, cmd)
                
        except subprocess.TimeoutExpired:
            self.logger.error("yamlresume command timed out")
            raise
        except FileNotFoundError:
            self.logger.error("yamlresume command not found. Please install yamlresume-cli")
            raise
        except Exception as e:
            self.logger.error(f"Error running yamlresume: {e}")
            raise
            
    def generate_resume(self, 
                       job_url: Optional[str] = None,
                       job_file: Optional[str] = None, 
                       keywords: Optional[str] = None):
        """Generate a tailored resume based on the provided options."""
        
        # Load personal data
        data_content = self.load_data_files()
        
        # Determine tailoring information
        tailoring_info = ""
        if job_url:
            job_description = self.fetch_job_description(job_url)
            tailoring_info = f"Tailor this resume for the following job posting:\n{job_description}"
        elif job_file:
            job_description = self.load_job_file(job_file)
            tailoring_info = f"Tailor this resume for the following job posting:\n{job_description}"
        elif keywords:
            tailoring_info = f"Tailor this resume to highlight these keywords and skills: {keywords}"
        else:
            tailoring_info = "Create a generic, professional resume."
            
        # Create prompt
        prompt = self.create_prompt(data_content, tailoring_info)
        
        # Call LLM
        llm_response = self.call_ollama(prompt)
        
        # Parse response
        resume_data = self.parse_llm_response(llm_response)
        
        # Save JSON
        self.save_json_resume(resume_data)
        
        # Convert to YAML
        yaml_file = self.convert_to_yaml(resume_data)
        
        # Build PDF
        self.build_pdf(yaml_file)
        
        self.logger.info("Resume generation completed successfully!")


def main():
    """Main function to handle CLI arguments and run the resume generator."""
    parser = argparse.ArgumentParser(
        description="Generate tailored resumes using Ollama LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python resume_generator.py                                    # Generic resume
  python resume_generator.py --job-url "https://example.com/job" # Tailored to job URL
  python resume_generator.py --job-file job.txt                 # Tailored to job file
  python resume_generator.py --keywords "Python, AI, ML"       # Tailored to keywords
  python resume_generator.py --slow --job-url "https://..."     # Use slower, more powerful model
        """
    )
    
    # Model selection
    parser.add_argument(
        '--slow', 
        action='store_true', 
        help='Use gpt-oss:120b instead of gpt-oss (slower but more powerful)'
    )
    
    # Tailoring options (mutually exclusive)
    tailoring_group = parser.add_mutually_exclusive_group()
    tailoring_group.add_argument(
        '--job-url', 
        type=str, 
        help='URL to job posting to tailor resume for'
    )
    tailoring_group.add_argument(
        '--job-file', 
        type=str, 
        help='Path to file containing job description'
    )
    tailoring_group.add_argument(
        '--keywords', 
        type=str, 
        help='Comma-separated keywords to highlight in resume'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.job_url and not args.job_url.startswith(('http://', 'https://')):
        print("Error: job-url must be a valid URL starting with http:// or https://")
        sys.exit(1)
        
    if args.job_file and not os.path.exists(args.job_file):
        print(f"Error: job file '{args.job_file}' not found")
        sys.exit(1)
        
    # Create and run generator
    try:
        generator = ResumeGenerator(slow_mode=args.slow)
        generator.generate_resume(
            job_url=args.job_url,
            job_file=args.job_file,
            keywords=args.keywords
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()