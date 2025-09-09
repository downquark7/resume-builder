#!/usr/bin/env python3
"""
Configuration file for Resume Builder

This file contains default settings and configurations for the resume builder.
Modify these values to customize the behavior of the script.
"""

# Default Ollama settings
DEFAULT_MODEL = "gpt-oss"
DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_TIMEOUT = 600  # 10 minutes
DEFAULT_CONTEXT_SIZE = 8192  # 8k context

# Model configurations
MODEL_CONFIGS = {
    "gpt-oss": {
        "temperature": 0.1,
        "top_p": 0.9,
        "top_k": 40,
        "num_ctx": 8192
    },
    "gpt-oss:120b": {
        "temperature": 0.1,
        "top_p": 0.9,
        "top_k": 40,
        "num_ctx": 8192
    },
    "gemma3:4b-it-q8_0": {
        "temperature": 0.2,
        "top_p": 0.9,
        "top_k": 40,
        "num_ctx": 4096
    }
}

# File paths
DATA_DIR = "data"
TEMPLATE_FILE = "template.json"
DEFAULT_OUTPUT = "resume.yaml"

# Resume generation settings
DEFAULT_CONCISE = True
MAX_WORK_EXPERIENCES_CONCISE = 4
MAX_WORK_EXPERIENCES_DETAILED = 6
MAX_SKILLS_CONCISE = 6
MAX_SKILLS_DETAILED = 8
MAX_PROJECTS_CONCISE = 3
MAX_PROJECTS_DETAILED = 4
MAX_KEYWORDS_PER_SKILL = 4
MAX_BULLETS_CONCISE = 3
MAX_BULLETS_DETAILED = 4

# Supported file extensions
SUPPORTED_EXTENSIONS = [".txt"]

# Error messages
ERROR_MESSAGES = {
    "ollama_connection": "Could not connect to Ollama. Make sure Ollama is running on localhost:11434",
    "yamlresume_not_found": "yamlresume not found. Please install it first.",
    "data_dir_not_found": "Data directory not found. Please create 'data/' directory with your information files.",
    "template_not_found": "Template file not found. Please ensure 'template.json' exists.",
    "job_file_not_found": "Job file not found. Please check the file path.",
    "json_parse_error": "Error parsing JSON response from AI model.",
    "yaml_save_error": "Error saving YAML file.",
    "pdf_build_error": "Error building PDF with yamlresume."
}

# Success messages
SUCCESS_MESSAGES = {
    "resume_generated": "Resume generated successfully!",
    "pdf_built": "PDF built successfully!",
    "yaml_saved": "YAML file saved successfully!",
    "setup_complete": "Setup verification completed successfully!"
}

# Debug settings
DEBUG_MODE = False
SAVE_DEBUG_JSON = True
DEBUG_FILE = "debug_resume.json"

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# API settings
REQUEST_TIMEOUT = (30, 600)  # (connection_timeout, read_timeout)
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Output settings
DEFAULT_PDF_TEMPLATE = "moderncv-banking"
DEFAULT_FONT_SIZE = "11pt"
DEFAULT_MARGINS = {
    "top": "2.5cm",
    "left": "1.5cm", 
    "right": "1.5cm",
    "bottom": "2.5cm"
}

# Validation settings
MIN_FILE_SIZE = 10  # bytes
MAX_FILE_SIZE = 1024 * 1024  # 1MB
REQUIRED_DATA_FILES = [
    "contact information.txt",
    "degree information.txt", 
    "work history information.txt",
    "skills.txt",
    "projects.txt",
    "classes taken.txt",
    "extracurriculars information.txt"
]

# Resume sections order
RESUME_SECTIONS = [
    "basics",
    "location", 
    "profiles",
    "education",
    "work",
    "languages",
    "skills",
    "awards",
    "certificates",
    "publications",
    "references",
    "projects",
    "interests",
    "volunteer"
]

# Date formats
DATE_FORMATS = [
    "MMM d, yyyy",  # Jan 1, 2024
    "MMM yyyy",     # Jan 2024
    "yyyy-MM",      # 2024-01
    "MM/yyyy",      # 01/2024
    "MMM d yyyy"    # Jan 1 2024
]

# Common skill categories
SKILL_CATEGORIES = [
    "Programming Languages",
    "Frameworks & Libraries", 
    "Tools & Technologies",
    "Cloud Platforms",
    "Databases",
    "Development Practices",
    "Soft Skills",
    "Certifications"
]

# Common job keywords for better tailoring
COMMON_KEYWORDS = {
    "software_engineer": [
        "Python", "Java", "JavaScript", "C++", "React", "Node.js",
        "Git", "Docker", "AWS", "Agile", "Scrum", "CI/CD"
    ],
    "data_scientist": [
        "Python", "R", "SQL", "Machine Learning", "TensorFlow", "Pandas",
        "NumPy", "Scikit-learn", "Jupyter", "Statistics", "Data Analysis"
    ],
    "devops": [
        "Docker", "Kubernetes", "AWS", "Azure", "Jenkins", "GitLab CI",
        "Terraform", "Ansible", "Monitoring", "Linux", "Bash"
    ],
    "frontend": [
        "React", "Vue.js", "Angular", "JavaScript", "TypeScript", "CSS",
        "HTML", "Webpack", "Babel", "SASS", "Responsive Design"
    ],
    "backend": [
        "Python", "Java", "Node.js", "Django", "Flask", "Spring Boot",
        "REST API", "GraphQL", "Microservices", "PostgreSQL", "MongoDB"
    ]
}
