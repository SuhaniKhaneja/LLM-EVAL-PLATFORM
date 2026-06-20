# LLM Evaluation Platform

Most teams building LLM applications have no systematic way to measure 
if their model is actually performing well. This platform automates that 
— every response gets scored, stored, and surfaced through a live dashboard.

**Live Demo:** https://llm-eval-platform-xz5k2xgthctg3na4j8rtn4.streamlit.app/

---

## What it does

Submit any prompt → Groq Llama 3.1 generates a response → 
the evaluation engine scores it across 4 dimensions → 
results are stored and queryable instantly.

Every evaluation returns:
- **ROUGE-1** — text similarity against a reference answer
- **Toxicity score** — automated detection via Detoxify
- **Length score** — appropriateness of response length
- **Composite score** — weighted overall quality

---

## Why I built it

At my internship, I was manually evaluating 10,000+ LLM outputs 
across 8 quality benchmarks. It was slow, inconsistent, and didn't 
scale. I built this so that evaluation becomes infrastructure, 
not a manual chore.

---

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | FastAPI (async)                   |
| Frontend   | Streamlit                         |
| LLM        | Groq Llama 3.1                    |
| Database   | SQLite + Async SQLAlchemy         |
| Validation | Pydantic                          |
| NLP        | rouge-score, Detoxify             |
| Deployed   | Render (backend) + Streamlit Cloud|

---

## API Endpoints

| Method | Endpoint          | Description         |
|--------|-------------------|---------------------|
| POST   | /api/v1/evaluate  | Evaluate a prompt   |
| GET    | /api/v1/logs      | Full evaluation history |
| GET    | /api/v1/metrics   | Aggregate metrics   |
| GET    | /health           | Health check        |

API Docs: https://llm-eval-platform-lfg1.onrender.com/docs

---

## What's next

- LLM-as-a-Judge scoring
- Semantic similarity via sentence-transformers  
- Multi-model comparison mode
- Batch evaluation + CSV/PDF export

---

## Note

Hosted on free-tier services. The first request after inactivity may take some time while the backend wakes up..
