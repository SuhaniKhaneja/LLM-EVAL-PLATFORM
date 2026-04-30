# LLM Evaluation Platform

A full-stack system for evaluating Large Language Model responses using automated quality metrics. Built with FastAPI, async SQLAlchemy, and Streamlit.

---

## What It Does

Most LLM projects skip evaluation. This platform makes it systematic — every response gets scored across four metrics, stored in a database, and served through a REST API and a dashboard.

**Pipeline:**
```
User Input → FastAPI → LLM → Evaluation Engine → SQLite → Metrics API → Streamlit UI
```

---

## Features

- **Evaluate** any LLM response against a reference answer
- **4 Metrics computed per evaluation:**
  - ROUGE-1 similarity score
  - Toxicity detection (binary)
  - Length score
  - Composite overall score
- **REST API** with `/evaluate`, `/logs`, and `/metrics` endpoints
- **Streamlit dashboard** — Evaluate, Logs, and Metrics tabs
- **Async backend** — handles concurrent requests without blocking
- **Persistent storage** via async SQLAlchemy + SQLite

---

## Tech Stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| Backend    | FastAPI (async)                      |
| ORM / DB   | Async SQLAlchemy + SQLite            |
| Frontend   | Streamlit                            |
| NLP        | rouge-score, detoxify                |
| Validation | Pydantic                             |

---

## Project Structure

```
llm-eval-platform/
├── app/
│   ├── main.py           # FastAPI entry point
│   ├── routes/           # API route handlers
│   ├── services/         # Business logic + evaluation engine
│   ├── schemas/          # Pydantic models
│   └── db/               # Async SQLAlchemy setup
├── frontend/
│   └── app.py            # Streamlit UI
├── requirements.txt
└── README.md
```

---

## Setup

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/llm-eval-platform.git
cd llm-eval-platform

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python -m app.db.init_db

# 5. Start backend
uvicorn app.main:app --reload --port 8000

# 6. Start frontend (new terminal)
streamlit run frontend/app.py
```

**API docs:** http://localhost:8000/docs  
**Streamlit UI:** http://localhost:8501

---

## API Endpoints

| Method | Endpoint    | Description                              |
|--------|-------------|------------------------------------------|
| POST   | /evaluate   | Submit response + reference → get scores |
| GET    | /logs       | Paginated evaluation history             |
| GET    | /metrics    | Aggregated stats (mean scores, toxicity) |
| GET    | /health     | API + DB health check                    |

---

## Why This Project

Evaluation is the hardest part of building with LLMs. This platform implements a repeatable, automated evaluation pipeline — the same pattern used in production ML systems — rather than relying on manual spot-checks.

---

## Roadmap

- [ ] LLM-as-judge for factual accuracy scoring
- [ ] Semantic similarity via sentence-transformers
- [ ] Batch evaluation endpoint
- [ ] Model comparison mode (same prompt, multiple backends)

---

## License

MIT
