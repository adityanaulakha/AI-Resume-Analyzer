
# AI Resume Analyzer (Demo-Ready)

A minimal demo of a resume-to-JD skill matcher using Flask. It supports PDF (via PyMuPDF) **and** TXT uploads to simplify presentations. Includes Dockerfile and a Jenkins pipeline (Jenkinsfile) to showcase CI/CD.

## Quick Start (Local)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 and upload a resume (.pdf or .txt) + paste a JD to see the match score.

> If PDF parsing fails on your machine, convert your resume to .txt for the demo.

## Run Tests

```bash
pip install pytest
pytest -q
```

## Docker

```bash
docker build -t ai-resume-analyzer:demo .
docker run -p 5000:5000 ai-resume-analyzer:demo
# Open http://localhost:5000
```

## Jenkins CI/CD

1. Run Jenkins (Docker):
   ```bash
   docker run -d -p 8080:8080 -p 50000:50000 --name jenkins jenkins/jenkins:lts
   ```
2. Install plugins: Pipeline, Docker Pipeline.
3. Add credentials:
   - ID: `dockerhub-creds-id` (Docker Hub Username/Password)
4. Create a Pipeline job using this repo (Jenkinsfile included).
5. Pipeline: Checkout → Install Deps → Tests → Docker Build → Push → Deploy (placeholder).

## How it works

- Extracts text from PDF/TXT.
- Tokenizes & normalizes words.
- Uses `data/skills_master.txt` to detect skills.
- Computes overlap-based match percentage between JD and resume.
