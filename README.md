# 🚀 CareerPilot AI

> AI-powered Career Assistant that helps users discover jobs, analyze resumes, and receive personalized job recommendations.

---

## 📌 Overview

CareerPilot AI simplifies the job search process by combining live job aggregation with Large Language Models (LLMs).

Users can:

- Upload their resume
- Receive AI-powered resume analysis
- Search jobs using natural language
- Get personalized job recommendations
- Apply directly using provided job links

---

# ✨ Features

## 🤖 AI Resume Analysis

- Upload PDF/DOCX resumes
- Extract candidate profile using Groq LLM
- Detect:
  - Skills
  - Programming Languages
  - Frameworks
  - Tools
  - Projects
  - Suggested Roles

---

## 💼 Resume-Based Job Recommendation

CareerPilot compares extracted resume information with available job postings.

Recommendations include:

- Match Score
- Matched Skills
- Company
- Location
- Salary
- Apply Link

---

## 🔍 AI Job Search

Search jobs naturally.

Example:

> Find me Python internships in Bangalore

> Remote Machine Learning jobs

The assistant interprets the request and returns relevant opportunities.

---

## 🌍 Live Job Aggregation

Current source

- Adzuna

Future integrations

- Remotive
- ArbeitNow
- RemoteOK

---

# 🏗 Architecture

```
                Streamlit Frontend
                        │
                        ▼
                 FastAPI Backend
        ┌────────────┼────────────┐
        ▼            ▼            ▼
 Resume AI      Job Search    Job Matcher
        │            │            │
        └────────────┼────────────┘
                     ▼
                 SQLite Database
                     ▼
                 Adzuna API
                     ▼
                  Groq LLM
```

---

# 🛠 Tech Stack

### Backend

- FastAPI
- SQLAlchemy
- SQLite
- REST APIs

### Frontend

- Streamlit

### AI

- Groq LLM

### Resume Processing

- PyMuPDF
- python-docx

### APIs

- Adzuna Job Search API

---

# 📂 Project Structure

```
backend/
│
├── api/
│   ├── jobs.py
│   ├── resume.py
│   ├── matcher.py
│   └── chat.py
│
├── services/
│   ├── ingestion.py
│   ├── resume_parser.py
│   ├── resume_analyzer.py
│   ├── job_matcher.py
│   └── query_parser.py
│
├── sources/
│   └── adzuna.py
│
├── database.py
├── models.py
└── main.py

frontend/
└── streamlit_app.py
```

---

# 🚀 Installation

Clone

```bash
git clone https://github.com/<your-username>/CareerPilot-AI.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env`

```
GROQ_API_KEY=YOUR_KEY

GROQ_MODEL=openai/gpt-oss-120b

ADZUNA_APP_ID=YOUR_APP_ID

ADZUNA_APP_KEY=YOUR_APP_KEY
```

---

# Run Backend

```bash
uvicorn backend.app.main:app --reload
```

---

# Run Frontend

```bash
streamlit run frontend/streamlit_app.py
```

---

# Current Features

- AI Resume Analysis
- Resume Parsing (PDF/DOCX)
- Resume-Based Job Matching
- Natural Language Job Search
- Live Job Aggregation
- Direct Apply Links

---

# Planned Features

- Career Mentor
- Multi-source Job Aggregation
- Resume Tailoring
- Cover Letter Generator
- Application Tracker
- PostgreSQL
- Docker Deployment

---

# Tech Highlights

- RESTful FastAPI backend
- Modular service architecture
- LLM-powered resume intelligence
- AI-assisted job search
- Skill-based recommendation engine

---

# Author

**Shivay Saurya**

B.Tech – Computational Mathematics

National Institute of Technology Agartala
