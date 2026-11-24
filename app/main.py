"""RoleFit Agent API: FastAPI + pgvector/Postgres or in-memory store,
Gemini LLM or the clearly-labelled demo stub.

Endpoints:
  GET  /health      — status, active store, active LLM/embedding providers
  GET  /jobs        — list the seeded jobs index (with optional filters)
  POST /chat        — one conversational turn; returns reply + ranked jobs
  POST /evaluate    — run the golden-set eval harness, return the report
  GET  /demo        — self-contained chat preview page (no build step)
  GET  /            — redirect to /demo

Seeded jobs are indexed on startup (idempotent), so the preview works
instantly with zero setup and zero keys. With GEMINI_API_KEY set the
agent uses real Gemini generation + embeddings; without it, it runs in
demo mode (stub LLM + hash embeddings), labelled as such in /health
and in every /chat response.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from .agent import Agent, build_agent
from .config import get_settings
from .demo import DEMO_HTML
from .eval import run_eval
from .models import ChatRequest, ChatResponse, EvalReport, Job


class HealthOut(BaseModel):
    status: str
    store: str
    llm_provider: str
    embedding_provider: str
    jobs_indexed: int
    demo_mode: bool


def create_app(agent: Agent | None = None) -> FastAPI:
    settings = get_settings()
    state: dict = {}

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        state["agent"] = agent or build_agent(settings)
        state["agent"].ensure_seeded()
        yield

    app = FastAPI(title="RoleFit Agent", version="0.1.0", lifespan=lifespan)

    def get_agent() -> Agent:
        return state["agent"]

    @app.get("/health", response_model=HealthOut)
    def health():
        ag = get_agent()
        demo = ag.llm.name == "stub-demo-only"
        return HealthOut(
            status="ok",
            store=ag.store.name,
            llm_provider=ag.llm.name,
            embedding_provider=ag.embedder.name,
            jobs_indexed=len(ag.store.list_jobs()),
            demo_mode=demo,
        )

    @app.get("/jobs", response_model=list[Job])
    def list_jobs(
        location: str | None = Query(default=None),
        employment_type: str | None = Query(default=None),
        work_mode: str | None = Query(default=None),
    ):
        ag = get_agent()
        jobs = ag.store.list_jobs()
        if location:
            jobs = [j for j in jobs if j.location.lower() == location.lower()]
        if employment_type:
            jobs = [
                j
                for j in jobs
                if j.employment_type.lower() == employment_type.lower()
            ]
        if work_mode:
            jobs = [j for j in jobs if j.work_mode.lower() == work_mode.lower()]
        return jobs

    @app.post("/chat", response_model=ChatResponse)
    def chat(request: ChatRequest):
        ag = get_agent()
        return ag.chat(request.session_id, request.message, top_k=request.top_k)

    @app.post("/evaluate", response_model=EvalReport)
    def evaluate():
        ag = get_agent()
        return run_eval(ag)

    @app.get("/demo", response_class=HTMLResponse)
    def demo():
        return DEMO_HTML

    @app.get("/")
    def root():
        return RedirectResponse(url="/demo")

    return app


app = create_app()
