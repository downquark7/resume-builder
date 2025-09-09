# Data Structure Examples

This document provides examples of how to structure your personal data files for the resume builder.

## 📁 Directory Structure

```
resume-builder/
├── data/
│   ├── contact information.txt
│   ├── degree information.txt
│   ├── work history information.txt
│   ├── skills.txt
│   ├── projects.txt
│   ├── classes taken.txt
│   └── extracurriculars information.txt
├── template.json
├── resume_builder.py
├── test_setup.py
└── requirements.txt
```

## 📝 File Examples

### contact information.txt
```
Name: John Smith
Email: john.smith@email.com
Phone: (555) 123-4567
GitHub: johnsmith
LinkedIn: linkedin.com/in/johnsmith
Website: johnsmith.dev
Location: San Francisco, CA
```

### degree information.txt
```
University of California, Berkeley
Bachelor of Science in Computer Science
Started: Fall 2018
Graduated: Spring 2022
GPA: 3.7
Relevant Coursework: Data Structures, Algorithms, Machine Learning, Database Systems
```

### work history information.txt
```
Senior Software Engineer
TechCorp Inc.
San Francisco, CA
January 2022 to Present
- Led development of microservices architecture serving 1M+ users
- Implemented CI/CD pipelines reducing deployment time by 50%
- Mentored 3 junior developers and conducted code reviews
- Collaborated with product team to define technical requirements

Software Engineer
StartupXYZ
Remote
June 2020 to December 2021
- Developed full-stack web applications using React and Node.js
- Built RESTful APIs handling 100K+ requests daily
- Optimized database queries improving response time by 40%
- Participated in agile development process with 2-week sprints

Software Development Intern
BigTech Corp
Seattle, WA
Summer 2019
- Worked on internal tools using Python and Django
- Gained experience with version control and code collaboration
- Participated in team meetings and project planning
```

### skills.txt
```
Programming Languages:
- Python (Expert)
- JavaScript (Expert)
- Java (Advanced)
- C++ (Intermediate)
- SQL (Advanced)
- Go (Beginner)

Frameworks & Libraries:
- React (Expert)
- Node.js (Advanced)
- Django (Advanced)
- Express.js (Advanced)
- TensorFlow (Intermediate)
- PyTorch (Intermediate)

Tools & Technologies:
- Git (Expert)
- Docker (Advanced)
- Kubernetes (Intermediate)
- AWS (Intermediate)
- Linux (Advanced)
- MongoDB (Advanced)
- PostgreSQL (Advanced)

Cloud Platforms:
- AWS (EC2, S3, Lambda, RDS)
- Google Cloud Platform (Compute Engine, Cloud Storage)
- Azure (Virtual Machines, App Service)

Development Practices:
- Agile/Scrum
- Test-Driven Development
- Code Review
- Continuous Integration/Deployment
- Microservices Architecture
```

### projects.txt
```
E-Commerce Platform
https://github.com/johnsmith/ecommerce-platform
January 2023 to March 2023
- Built full-stack e-commerce application using React and Node.js
- Implemented payment processing with Stripe API
- Created admin dashboard for inventory management
- Deployed on AWS with Docker containers
- Technologies: React, Node.js, MongoDB, Stripe, AWS, Docker

Machine Learning Model for Image Classification
https://github.com/johnsmith/image-classifier
September 2022 to November 2022
- Developed CNN model for classifying medical images
- Achieved 94% accuracy on test dataset
- Created web interface for model inference
- Technologies: Python, TensorFlow, OpenCV, Flask

Task Management API
https://github.com/johnsmith/task-api
June 2022 to July 2022
- RESTful API for task management with user authentication
- Implemented JWT tokens and password hashing
- Added real-time notifications using WebSockets
- Technologies: Python, Django, PostgreSQL, Redis, WebSockets
```

### classes taken.txt
```
Computer Science Core:
- CS 61A: Structure and Interpretation of Computer Programs
- CS 61B: Data Structures
- CS 61C: Machine Structures
- CS 170: Efficient Algorithms and Intractable Problems
- CS 162: Operating Systems and System Programming
- CS 186: Introduction to Database Systems

Mathematics:
- MATH 1A: Calculus
- MATH 1B: Calculus
- MATH 54: Linear Algebra and Differential Equations
- STAT 134: Concepts of Probability

Specialized Courses:
- CS 188: Introduction to Artificial Intelligence
- CS 189: Introduction to Machine Learning
- CS 161: Computer Security
- CS 164: Programming Languages and Compilers
```

### extracurriculars information.txt
```
Hackathon Participation
UC Berkeley
2019-2022
- Participated in 8 hackathons, winning 3 first-place prizes
- Developed mobile app for campus navigation (CalHacks 2019)
- Created AI-powered study tool (Hack the North 2021)
- Led team of 4 developers in 48-hour coding competitions

Computer Science Club
UC Berkeley
2018-2022
- Served as Vice President (2021-2022)
- Organized weekly coding workshops for 50+ members
- Hosted guest speakers from tech companies
- Mentored new members in programming fundamentals

Open Source Contributions
GitHub
2020-Present
- Contributed to 15+ open source projects
- Maintained popular Python library with 1K+ stars
- Reviewed pull requests and helped new contributors
- Technologies: Python, JavaScript, Go, Rust

Volunteer Tutoring
Local High School
2021-2022
- Taught programming basics to high school students
- Created curriculum for 12-week coding bootcamp
- Helped 20+ students learn Python and web development
- Received recognition from school administration
```

## 💡 Tips for Better Results

### 1. Be Specific and Quantified
Instead of:
```
- Worked on web development
```

Write:
```
- Developed React application serving 10K+ daily users
- Reduced page load time by 30% through code optimization
```

### 2. Use Action Verbs
- Led, Developed, Implemented, Optimized, Created, Designed
- Collaborated, Mentored, Managed, Analyzed, Improved

### 3. Include Relevant Keywords
- Match terminology from job descriptions
- Use industry-standard terms
- Include specific technologies and tools

### 4. Keep It Current
- Update regularly with new experiences
- Remove outdated information
- Focus on recent and relevant achievements

### 5. Be Consistent
- Use consistent date formats (Month Year)
- Maintain consistent formatting across files
- Keep similar information grouped together

## 🔄 Updating Your Data

When updating your data files:

1. **Add new experiences** to work history
2. **Update skills** with new technologies
3. **Include new projects** with descriptions
4. **Refresh contact information** if needed
5. **Add recent coursework** or certifications

The resume builder will automatically incorporate all changes when generating new resumes.

## 📋 Data Validation

Before running the resume builder, ensure:

- [ ] All required files exist in `data/` directory
- [ ] Files contain relevant, up-to-date information
- [ ] No sensitive information is included (use placeholder data for examples)
- [ ] File names match exactly (case-sensitive)
- [ ] All files have `.txt` extension
- [ ] Content is well-formatted and readable

## 🚀 Quick Start Checklist

1. Create `data/` directory
2. Add all 7 required text files with your information
3. Run `python test_setup.py` to verify setup
4. Generate your first resume: `python resume_builder.py --build-pdf`
5. Review and refine your data files as needed
6. Regenerate resume with improvements
