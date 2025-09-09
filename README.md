# Resume Builder

A powerful AI-powered resume builder that creates tailored, professional resumes using local data and job descriptions.

## 🚀 Features

- **AI-Powered Content Generation**: Uses Ollama with GPT-OSS models for intelligent resume creation
- **Multiple Input Sources**: Supports job descriptions from files, URLs, or keywords
- **Flexible Output**: Generates both YAML and PDF formats
- **Tailored Content**: Automatically customizes resumes based on job requirements
- **Conciseness Control**: Choose between concise (default) or detailed resume formats
- **8k Context Support**: Handles comprehensive personal data and job descriptions
- **Local Processing**: All data stays on your machine for privacy

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- Ollama running locally (localhost:11434)
- yamlresume installed globally

### Python Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `requests>=2.25.0` - HTTP requests for Ollama API
- `PyYAML>=6.0` - YAML file processing

## 🛠️ Installation

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd resume-builder
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install Ollama**
   - Download from [ollama.ai](https://ollama.ai)
   - Install and start the service
   - Pull the desired model: `ollama pull gpt-oss`

4. **Install yamlresume**
   ```bash
   npm install -g yamlresume
   ```

5. **Prepare your data**
   - Create a `data/` directory
   - Add your personal information as text files (see Data Structure below)

## 📁 Data Structure

The script expects personal data in the `data/` directory as plain text files:

```
data/
├── contact information.txt    # Name, email, phone, GitHub, etc.
├── degree information.txt     # Education details
├── work history information.txt # Employment history
├── skills.txt                # Technical skills and expertise
├── projects.txt              # Personal and professional projects
├── classes taken.txt         # Relevant coursework
└── extracurriculars information.txt # Activities and achievements
```

### Example Data Files

**contact information.txt:**
```
Name: John Doe
Email: john.doe@email.com
Phone: (555) 123-4567
GitHub: johndoe
LinkedIn: linkedin.com/in/johndoe
```

**work history information.txt:**
```
Software Engineer - Tech Corp
Remote
June 2022 to Present
- Developed web applications using Python and React
- Led team of 3 developers on major project
- Improved system performance by 40%

Data Analyst - Data Inc
New York, NY
January 2020 to May 2022
- Analyzed large datasets using SQL and Python
- Created automated reporting dashboards
- Reduced reporting time by 60%
```

## 🚀 Quick Start

1. **Set up your data** (see Data Structure section below)
2. **Test your setup**: `python test_setup.py`
3. **Generate your first resume**: `python resume_builder.py --job-file job.txt --build-pdf`

## 🚀 Usage

### Basic Usage

```bash
# Generate resume with job file
python resume_builder.py --job-file job.txt --build-pdf

# Generate resume with keywords
python resume_builder.py --job-keywords "Python, Machine Learning, Data Science" --build-pdf

# Generate resume without job tailoring
python resume_builder.py --build-pdf
```

### Advanced Usage

```bash
# Use different Ollama model
python resume_builder.py --job-file job.txt --model gpt-oss:120b --build-pdf

# Generate detailed resume (more comprehensive)
python resume_builder.py --job-file job.txt --detailed --build-pdf

# Generate concise resume (default, shorter and focused)
python resume_builder.py --job-file job.txt --concise --build-pdf

# Custom output file
python resume_builder.py --job-file job.txt --output my_resume.yaml --build-pdf

# Fetch job description from URL
python resume_builder.py --job-url "https://example.com/job-posting" --build-pdf
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--job-file FILE` | Path to job description file | None |
| `--job-url URL` | URL to fetch job description from | None |
| `--job-keywords TEXT` | Keywords for job tailoring | None |
| `--model MODEL` | Ollama model to use | `gpt-oss` |
| `--output FILE` | Output YAML file | `resume.yaml` |
| `--build-pdf` | Build PDF after creating YAML | False |
| `--concise` | Generate concise resume | True |
| `--detailed` | Generate detailed resume | False |

**Note:** `--job-file`, `--job-url`, and `--job-keywords` are mutually exclusive. Only one can be used at a time.

## 📊 Output Formats

### YAML Output
The script generates a YAML file compatible with yamlresume:
```yaml
content:
  basics:
    name: John Doe
    email: john.doe@email.com
    # ... more fields
  work:
    - name: Tech Corp
      position: Software Engineer
      # ... more fields
  # ... other sections
```

### PDF Output
When using `--build-pdf`, the script automatically generates a professional PDF resume using yamlresume.

## 🔧 Configuration

### Ollama Models
The script supports various Ollama models:
- `gpt-oss` (default) - Good balance of speed and quality
- `gpt-oss:120b` - Larger model for more complex tasks
- `gemma3:4b-it-q8_0` - Smaller, faster model
- Any other Ollama model you have installed

### Context Size
The script is configured for 8k context size by default, allowing it to process comprehensive personal data and job descriptions.

## 🧪 Testing

Test your setup with the included test script:

```bash
python test_setup.py
```

This will verify:
- Data files are present
- Template is valid
- Ollama connection works
- yamlresume is installed

## 📝 Examples

### Example 1: Software Engineer Position
```bash
python resume_builder.py --job-file software_engineer_job.txt --build-pdf
```

### Example 2: Data Science Keywords
```bash
python resume_builder.py --job-keywords "Python, Machine Learning, TensorFlow, Data Analysis" --build-pdf
```

### Example 3: Detailed Resume
```bash
python resume_builder.py --job-file job.txt --detailed --build-pdf
```

## 🐛 Troubleshooting

### Common Issues

**"Could not connect to Ollama"**
- Ensure Ollama is running: `ollama serve`
- Check if it's accessible: `curl http://localhost:11434/api/tags`

**"yamlresume not found"**
- Install yamlresume: `npm install -g yamlresume`
- Verify installation: `yamlresume --version`

**"No module named 'requests'"**
- Install dependencies: `pip install -r requirements.txt`

**"Data directory not found"**
- Create `data/` directory and add your text files
- Ensure files have `.txt` extension

**"JSON parsing error"**
- The AI model may have generated malformed JSON
- Check `debug_resume.json` for the problematic output
- Try with a different model or regenerate

### Debug Mode
If you encounter issues, the script saves problematic JSON to `debug_resume.json` for inspection.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source. See the LICENSE file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for local AI model hosting
- [yamlresume](https://yamlresume.dev) for PDF generation
- The open source community for inspiration and tools

## 📞 Support

If you encounter issues or have questions:
1. Check the troubleshooting section above
2. Review the test setup output
3. Check the debug files if available
4. Open an issue with detailed error information

---

**Version:** 1.0.0  
**Author:** AI Assistant  
**Last Updated:** 2024
