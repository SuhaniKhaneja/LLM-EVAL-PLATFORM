# LLM Evaluation Platform

Most teams building LLM applications have no systematic way to measure
if their model is actually performing well. This platform automates that:
every response is scored, stored, and surfaced through a live dashboard.

**Live demo:** <https://llm-eval-platform-xz5k2xgthctg3na4j8rtn4.streamlit.app/>
**API docs:** <https://llm-eval-platform-lfg1.onrender.com/docs>

> Hosted on free-tier services. The first request after inactivity may take
> a while while the backend wakes up.

---

## What it does

Submit a prompt, and the platform:

1. Sends it to an LLM (Groq, model `openai/gpt-oss-20b`)
2. Scores the response with a rule-based evaluation engine
3. Stores the prompt, response, and scores in a database
4. Shows results in a dashboard with a log history and aggregate metrics

Every evaluation returns:

| Score | What it measures |
|---|---|
| **ROUGE-1** | Word overlap between the response and a reference answer (F-measure) |
| **Length score** | Whether the response length is reasonable (0 to 1) |
| **Toxicity flag** | Rule-based pattern check: clean (1.0) or toxic (0.0) |
| **Overall score** | Weighted composite, 0 to 100 |

---

## Why I built it

At my internship, I was manually evaluating 10,000+ LLM outputs across
8 quality benchmarks. It was slow, inconsistent, and didn't scale. I built
this so that evaluation becomes infrastructure, not a manual chore.

---

## How scoring works

```
overall = (length * 0.25 + rouge1 * 0.40 + toxicity * 0.35) * 100
```

- **Length:** under 50 characters scores low (ramps up to 0.3), 50 to 100
  ramps from 0.3 to 0.7, 100 to 1500 characters scores 1.0, and longer
  responses are gradually penalized down to 0.6.
- **ROUGE-1:** computed with the `rouge-score` library (with stemming).
  If no reference is provided, it falls back to the first 80 characters of
  the response itself, so the score is only meaningful when you supply a
  reference.
- **Toxicity:** a set of regex patterns (self-harm phrases, slurs,
  bomb-making, "how to hack/ddos"). Any match sets the score to 0.0 and
  flags the response as toxic; otherwise 1.0.
- **Weights** are fixed starting values, not tuned against human judgments.

The dashboard groups overall scores into buckets:
poor (< 40), fair (40 to 60), good (60 to 80), excellent (80+).

---

## Architecture

```
Streamlit UI  --HTTP-->  FastAPI  -->  llm_service  -->  Groq API
                            |
                            +--> evaluation engine (length, ROUGE-1, toxicity)
                            |
                            +--> SQLite (async SQLAlchemy)
```

Flow of a single request (`POST /api/v1/evaluate`):

1. The route validates the request with Pydantic.
2. `eval_service.run_evaluation` calls the LLM through `llm_service.call_llm`,
   which also records latency and token usage.
3. `scorer.compute_scores` runs the three scorers and combines them.
4. A `Prompt`, `Response`, and `EvalResult` row are saved, linked by
   foreign keys.
5. The full result is returned to the caller.

If the LLM call or scoring fails, the API returns HTTP 502.

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (async) |
| Frontend | Streamlit |
| LLM | Groq API via the OpenAI SDK (`openai/gpt-oss-20b`) |
| Database | SQLite + async SQLAlchemy (aiosqlite) |
| Validation / config | Pydantic, pydantic-settings |
| Scoring | rouge-score, custom regex toxicity filter |
| Deployment | Render (backend, auto-deploy from `main`) + Streamlit Cloud (frontend) |

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/evaluate` | Evaluate a prompt |
| GET | `/api/v1/logs` | Paginated evaluation history (`page`, `page_size` up to 100) |
| GET | `/api/v1/metrics` | Aggregate metrics |
| GET | `/health` | Health check |

**Request body for `/evaluate`:**

```json
{
  "prompt": "Explain what an API is.",
  "reference": "An API lets two programs talk to each other.",
  "max_tokens": 512
}
```

`prompt` is required (1 to 4000 characters), `reference` is optional, and
`max_tokens` ranges from 1 to 4096 (default 512).

`/metrics` returns total evaluations, average score, average latency,
toxic count and rate, average ROUGE-1, and the score distribution.

---

## Data model

Three tables, linked one-to-one down the chain:

`Prompt` -> `Response` (text, model, latency, token counts) -> `EvalResult`
(length, ROUGE-1, toxicity, is_toxic, overall score)

Tables are created automatically on startup.

---

## Run locally

```bash
# 1. Install and configure
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=any_placeholder   # currently required by config.py, not used for LLM calls
```

```bash
# 2. Start the backend
uvicorn app.main:app --reload

# 3. Start the frontend (in a second terminal)
pip install -r requirements-frontend.txt
API_URL=http://localhost:8000 streamlit run frontend/app.py
```

---

## Project structure

```
app/
  main.py                 # FastAPI app, router wiring, DB init on startup
  api/routes/             # evaluate, logs, metrics endpoints
  services/
    llm_service.py        # Groq call, latency and token capture
    eval_service.py       # orchestration + logs and metrics queries
  evaluation/
    scorer.py             # weighted composite score
    length_scorer.py
    rouge_scorer.py
    toxicity_checker.py
  models/eval_models.py   # SQLAlchemy tables
  schemas/eval_schemas.py # Pydantic request/response models
  core/config.py          # settings from environment
  db/base.py              # async engine, session, init
frontend/app.py           # Streamlit dashboard (Evaluate, Logs, Metrics tabs)
render.yaml               # Render backend deployment config
```

---

## Known limitations

- Toxicity detection is a fixed regex list. It is fast and needs no model,
  but it only catches phrases it knows about and gives a binary result.
- ROUGE-1 measures word overlap, not meaning, and is not informative
  without a reference answer.
- Score weights are hand-chosen, not calibrated against human ratings.
- SQLite is simple but single-node; on free-tier hosting the database file
  may not persist across redeploys.

---

## What's next

- Replace the regex filter with a classifier (for example Detoxify) for
  probabilistic toxicity scores
- LLM-as-a-Judge scoring
- Semantic similarity via sentence-transformers
- Multi-model comparison mode
- Batch evaluation and CSV/PDF export
