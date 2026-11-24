# RoleFit Agent — a conversational LLM job-matcher

A person states what they want (and what they'd never take) in plain
words, over a conversation. An LLM agent with tool use and structured
outputs understands it, remembers context across turns, retrieves
matching roles from a jobs index, ranks them with a plain-words reason
for each, and refines as the person replies.

Built as the proof project for an agentic job-matching role: LLM agents
with tool use and memory, retrieval + ranking + personalisation,
semantic search over a jobs index, and an LLM eval harness. It is a
new codebase, not a copy of the earlier RAG demo — it reuses only the
proven patterns (FastAPI + pgvector + Gemini, with $0 fallbacks).

## How it works

One chat turn runs four steps:

1. **Extract** — the LLM (or a rule fallback) reads the message and
   returns a structured profile patch: wants, never-takes, skills,
   places, pay floor, type, mode.
2. **Remember** — the patch merges into the session profile, kept
   across turns. The agent doesn't re-ask what it already knows.
3. **Tool use** — the agent builds a search query from the profile and
   calls its `search_jobs` tool: semantic search over the jobs index
   (pgvector or in-memory), then deterministic reranking. Deal-breakers
   are hard filters (a refused job never appears); everything else is
   a weighted score (0.40 vector similarity + 0.35 skill overlap +
   0.25 preference fit) with a plain-words reason attached.
4. **Answer** — the LLM (or a template fallback) writes the reply from
   the tool results only, one reason per job.

## Providers and modes

| Piece | With `GEMINI_API_KEY` set | Without a key (demo mode) |
|---|---|---|
| Generation | Gemini `gemini-3.6-flash`, JSON mode | Deterministic stub (rule extraction + templated replies) |
| Embeddings | Gemini `gemini-embedding-001`, 3072 dims | Deterministic hash embeddings |
| Store | Postgres + pgvector (`STORE=postgres`) or memory | In-memory |

Demo mode is labelled `stub-demo-only` / `fallback-demo-only` in
`/health` and in every `/chat` response. It is never presented as a
real LLM.

Verified live 24 Nov 2026: `gemini-3.6-flash` generation with JSON
structured output works, the extract and compose prompts return valid
JSON, and `gemini-embedding-001` embeds fine (3072 dims).
`text-embedding-004` returns 404 for this key, so it is not the
default — don't switch back without re-checking.

## Eval

`python -m app.eval` (or `POST /evaluate`) runs 11 golden cases —
persona messages in, expected jobs out — and reports hit@3, MRR@5 and
deal-breaker violations.

Measured 24 Nov 2026, stub providers (deterministic, no key):
**hit@3 1.00, MRR@5 1.00, violations 0** — every expected job ranked
first. Run it again after any ranking change; it is also the
`test_eval.py` gate in the test suite.

## Run it

Local, one command (no database, no key — demo mode):

```bash
./scripts/run_local.sh
# or: make run
```

With a real Gemini key:

```bash
cp .env.example .env   # put your key in .env, never commit it
./scripts/run_local.sh
```

Docker (app + pgvector Postgres):

```bash
cp .env.example .env   # set GEMINI_API_KEY for the real LLM path
docker compose up --build
```

Then open http://localhost:8000/demo — a chat UI with example prompts.

Deploy notes: the app is a plain FastAPI service. On Render, use the
Dockerfile with a managed Postgres + the `pgvector` extension, or
deploy the API alone with `STORE=memory` (the seeded index loads on
startup either way). No deploy is included here — the live deploy is a
one-tap step for the repo owner.

## API

- `GET /health` — status, active store/LLM/embedding providers, jobs indexed
- `GET /jobs` — list the seeded index (`?location=`, `?employment_type=`, `?work_mode=`)
- `POST /chat` — `{"message": "...", "session_id": "...", "top_k": 5}` → reply + ranked jobs + profile
- `POST /evaluate` — run the golden-set eval harness
- `GET /demo` — chat preview page

## Tests

```bash
make test    # 32 pytest tests: ranking, extraction, agent, API, stores, eval gate
make eval    # golden-set eval report
```

## Honest limits

- The index is **30 fictional listings** written for this demo (see
  `app/seed_jobs.py`). No real job board was scraped, no real company
  or person is named, and there are no real users.
- Sessions live in memory; restarting the server forgets conversations.
  There is no auth — don't expose it publicly as-is.
- The Docker image and compose stack are written but were **not
  executed on this machine** (Docker is not installed here); the
  compose file parses, and the app itself was tested over HTTP.
  Likewise the Postgres + pgvector path is code-reviewed against the
  rag-demo's proven store, not live-tested here — run
  `docker compose up` to verify it end to end.
- Free-tier Gemini is rate-limited and can return 503 under load; the
  app surfaces the error rather than retrying in a loop.

## Layout

```
app/
  config.py      env-based settings (key from env only)
  models.py      typed models for jobs, profiles, agent I/O
  seed_jobs.py   30 fictional listings
  embeddings.py  Gemini + demo-only hash embedder
  store.py       PgVectorStore + InMemoryStore
  ranking.py     hard filters + weighted rerank + reasons
  extract.py     rule-based profile extraction (stub + fallback)
  llm.py         Gemini REST client + demo-only stub
  agent.py       the agent loop: extract → remember → tool → answer
  eval_cases.py  11 golden cases
  eval.py        eval harness (CLI + /evaluate)
  demo.py        chat preview page
  main.py        FastAPI app
tests/           32 pytest tests
scripts/         run_local.sh, smoke_gemini.py, live checks
```
