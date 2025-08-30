# AI Resume Analyzer 🚀

Interactive Streamlit app that compares a candidate's resume with a job description using Google Gemini. It extracts skills, highlights matches & gaps, computes a match percentage, and produces a summarized assessment. Includes Docker & Jenkins pipeline for automated CI/CD.

### Features
* PDF & TXT resume upload (PDF parsed via `pdfplumber`).
* AI-powered structured analysis (Gemini → enforced JSON schema).
* Sections: Matched Skills, Missing Skills, Match %, Summary.
* Detail level selector (Concise / Standard / Detailed).
* Download results as JSON or Markdown.
* Robust parser with graceful fallback if model deviates from JSON.
* Tests for response parsing.
* Dockerfile + Jenkinsfile for automated build/test/push.

---
### 1. Prerequisites
* Python 3.10+
* Google Gemini API key (set `GEMINI_API_KEY` in a `.env` file)
* (Optional) Docker & Jenkins for CI/CD

`.env` example:
```
GEMINI_API_KEY=your_gemini_key_here
```

---
### 2. Local Run (Streamlit)
```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```
Open: http://localhost:8501

---
### 3. Run Tests
```powershell
pytest -q
```

---
### 4. Docker Usage
Build & run (exposes Streamlit on 8501 inside container; we map to 8501):
```powershell
docker build -t ai-resume-analyzer:latest .
docker run -p 8501:8501 --env GEMINI_API_KEY=$Env:GEMINI_API_KEY ai-resume-analyzer:latest
```
If the image still exposes port 5000 (legacy), change the `EXPOSE` and entrypoint accordingly or map 5000.

---
### 5. Jenkins Pipeline (CI/CD)
Pipeline stages (see `Jenkinsfile`):
1. Checkout
2. Create venv & install deps + pytest
3. Run tests
4. Docker build
5. Docker login & push (needs creds id: `dockerhub-creds-id`)
6. Deploy placeholder (echo pull/run command)

Minimal Jenkins setup:
```bash
docker run -d -p 8080:8080 -p 50000:50000 --name jenkins jenkins/jenkins:lts
```
Add Docker inside Jenkins host (or use an agent with Docker).

Credentials: add Docker Hub username/password as `dockerhub-creds-id`.

---
### 6. Code Overview
| Component | Purpose |
|-----------|---------|
| `app.py` | Streamlit app + Gemini prompt + parsing/export |
| `data/skills_master.txt` | (Legacy) skills list; current logic relies on AI extraction |
| `Dockerfile` | Container build instructions |
| `Jenkinsfile` | CI/CD stages |
| `test_app.py` | Parser unit tests |

---
### 7. Adjusting AI Output
Use the Detail Level dropdown. It modifies:
* Note length per skill
* Summary depth

To further tune: edit `analyze_resume()` prompt constraints.

---
### 8. Environment Variables
| Var | Description |
|-----|-------------|
| `GEMINI_API_KEY` | Required for Gemini model calls |

Set inside `.env` (loaded via `python-dotenv`) or pass via Docker `--env`.

---
### 9. Future Improvements (Ideas)
* Add authentication (per-user history).
* Persist analyses (SQLite / PostgreSQL).
* Add model selection & temperature control.
* Export as PDF.
* Slack / Email integration for sharing results.

---
### 10. Troubleshooting
| Issue | Fix |
|-------|-----|
| API key missing | Create `.env` with `GEMINI_API_KEY` |
| Empty skills lists | Model failed JSON → fallback triggered; retry Detailed mode |
| Docker build slow | Enable build cache; pin dependencies |
| Jenkins Docker perms | Add user to `docker` group or use Docker-in-Docker agent |

---
### 11. Disclaimer
AI output may contain hallucinations; always validate critical decisions manually.

---

Happy analyzing! 🎯
