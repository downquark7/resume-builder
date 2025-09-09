# Quick Usage Guide

## 🎯 Get Started in 5 Minutes

### Step 1: Prepare Your Data
Create a `data/` folder and add these files with your information:

```
data/
├── contact information.txt    # Your name, email, phone, GitHub
├── degree information.txt     # Education details
├── work history information.txt # Your work experience
├── skills.txt                # Technical skills
├── projects.txt              # Personal/professional projects
├── classes taken.txt         # Relevant coursework
└── extracurriculars information.txt # Activities and achievements
```

### Step 2: Test Your Setup
```bash
python test_setup.py
```

### Step 3: Generate Your Resume
```bash
# With a job description file
python resume_builder.py --job-file job.txt --build-pdf

# With keywords
python resume_builder.py --job-keywords "Python, Machine Learning" --build-pdf

# Without job tailoring
python resume_builder.py --build-pdf
```

## 📝 Common Commands

| What you want to do | Command |
|---------------------|---------|
| Generate resume with job file | `python resume_builder.py --job-file job.txt --build-pdf` |
| Generate with keywords | `python resume_builder.py --job-keywords "Python, AI" --build-pdf` |
| Generate detailed resume | `python resume_builder.py --job-file job.txt --detailed --build-pdf` |
| Use different AI model | `python resume_builder.py --job-file job.txt --model gpt-oss:120b --build-pdf` |
| Just YAML (no PDF) | `python resume_builder.py --job-file job.txt` |
| Custom output name | `python resume_builder.py --job-file job.txt --output my_resume.yaml` |

## 🔧 Troubleshooting

**"Could not connect to Ollama"**
- Start Ollama: `ollama serve`
- Check if running: `curl http://localhost:11434/api/tags`

**"yamlresume not found"**
- Install: `npm install -g yamlresume`

**"Data directory not found"**
- Create `data/` folder and add your `.txt` files

**"No module named 'requests'"**
- Install dependencies: `pip install -r requirements.txt`

## 💡 Pro Tips

1. **Use specific, quantified achievements** in your work history
2. **Match keywords** from the job description in your skills
3. **Keep it concise** - the default setting works well for most jobs
4. **Update your data regularly** as you gain new experiences
5. **Test different models** if you want different writing styles

## 📁 File Examples

### contact information.txt
```
Name: Your Name
Email: your.email@example.com
Phone: (555) 123-4567
GitHub: yourusername
LinkedIn: linkedin.com/in/yourprofile
```

### work history information.txt
```
Software Engineer
Tech Company
City, State
January 2022 to Present
- Developed web applications using Python and React
- Led team of 3 developers on major project
- Improved system performance by 40%

Previous Job Title
Previous Company
City, State
June 2020 to December 2021
- Built RESTful APIs handling 100K+ requests daily
- Collaborated with product team on feature development
```

### skills.txt
```
Programming Languages:
- Python (Expert)
- JavaScript (Advanced)
- Java (Intermediate)

Frameworks:
- React (Expert)
- Django (Advanced)
- Node.js (Intermediate)

Tools:
- Git (Expert)
- Docker (Advanced)
- AWS (Intermediate)
```

That's it! You're ready to generate professional, tailored resumes. 🚀
