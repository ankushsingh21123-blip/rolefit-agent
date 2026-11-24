"""The RoleFit agent.

One chat turn runs four steps, and the LLM is involved in two of them:

1. EXTRACT — the LLM (or the rule fallback) reads the person's message
   and returns a structured ``ProfilePatch``: what they want, what
   they'd never take, skills, places, pay floor, type, mode.
2. REMEMBER — the patch is merged into the session profile, which is
   kept across turns. The agent remembers context instead of asking
   the same questions again.
3. TOOL USE — the agent builds a search query from the profile and
   calls its ``search_jobs`` tool: semantic search over the jobs index
   (pgvector or in-memory), then deterministic reranking with hard
   deal-breaker filters.
4. ANSWER — the LLM (or the template fallback) writes the reply from
   the tool results only, with one plain-words reason per job.

Nothing is invented: if the LLM's structured output cannot be parsed,
the rule extractor in extract.py runs instead, and if the reply cannot
be composed, a template built from the ranked jobs is used.
"""

import json
import uuid

from .config import Settings
from .embeddings import get_embedder
from .extract import extract_profile_rules
from .llm import get_llm
from .models import (
    ChatResponse,
    ChatTurn,
    PreferenceProfile,
    ProfilePatch,
    RankedJob,
    SearchToolArgs,
)
from .ranking import rerank
from .seed_jobs import SEED_JOBS
from .store import InMemoryStore, PgVectorStore

EXTRACT_PROMPT = """TASK: EXTRACT_PROFILE
You extract a job seeker's preferences from one chat message, as strict JSON.
Current profile (JSON): {profile}
Recent turns: {history}
USER MESSAGE:
{message}
END MESSAGE
Return ONLY this JSON object (no other text):
{{"wants_text": string or null, "role_keywords": [strings], "skills": [strings], "locations": [strings], "min_salary_monthly": integer or null, "employment_types": ["Full-time"|"Part-time"|"Internship"], "work_modes": ["Remote"|"On-site"|"Hybrid"], "never": [short deal-breaker phrases], "notes": [strings]}}
Rules: only include what the person actually stated in this message. Salary is monthly INR. Locations use city names or "Remote" — if the person says "remote", put "Remote" in BOTH locations and work_modes. "never" holds things they refuse, e.g. "sales", "night shift", "weekends"."""

COMPOSE_PROMPT = """TASK: COMPOSE_REPLY
You are RoleFit, a friendly job-matching agent. Write a short reply (3-5 sentences) to the job seeker, naming the matched jobs and giving one plain-words reason per job.
Seeker profile (JSON): {profile}
Matched jobs (JSON):
JOBS_JSON:
{jobs_json}
END JOBS_JSON
Return ONLY this JSON object: {{"reply": "..."}}
Rules: never invent jobs, salaries or skills. Use only the matched jobs given. If no jobs matched, say so honestly and ask one clarifying question."""


def _extract_json(raw: str) -> str:
    """Pull the first JSON object out of raw model text."""
    raw = raw.strip()
    try:
        json.loads(raw)
        return raw
    except json.JSONDecodeError:
        pass
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        return raw[start : end + 1]
    raise ValueError("no JSON object found in model output")


def _template_reply(profile: PreferenceProfile, ranked: list[RankedJob]) -> str:
    if not ranked:
        return (
            "I couldn't find a match for that yet in the jobs I know about. "
            "Could you tell me a bit more — for example the role, the place, "
            "or the minimum pay you'd accept?"
        )
    lines = ["Here are the closest matches I found for you:"]
    for item in ranked:
        job = item.job
        reason = item.reasons[0] if item.reasons else "Good match"
        lines.append(
            f"- {job.title} at {job.company} — {job.location}, "
            f"{job.work_mode}, {job.employment_type}, "
            f"₹{job.salary_min:,}–₹{job.salary_max:,} a month. {reason}."
        )
    lines.append(
        "Want me to narrow this down? Tell me what to change — role, "
        "place, pay, or something you'd never take."
    )
    return "\n".join(lines)


def merge_patch(profile: PreferenceProfile, patch: ProfilePatch) -> PreferenceProfile:
    """Merge a patch into a profile: lists union, salary overwrites when
    stated, wants_text updates when stated."""

    def union(existing: list[str], new: list[str]) -> list[str]:
        out = list(existing)
        for item in new:
            if item not in out:
                out.append(item)
        return out

    return PreferenceProfile(
        wants_text=patch.wants_text or profile.wants_text,
        role_keywords=union(profile.role_keywords, patch.role_keywords),
        skills=union(profile.skills, patch.skills),
        locations=union(profile.locations, patch.locations),
        min_salary_monthly=(
            patch.min_salary_monthly
            if patch.min_salary_monthly is not None
            else profile.min_salary_monthly
        ),
        employment_types=union(profile.employment_types, patch.employment_types),
        work_modes=union(profile.work_modes, patch.work_modes),
        never=union(profile.never, patch.never),
        notes=union(profile.notes, patch.notes),
    )


def build_search_query(profile: PreferenceProfile) -> str:
    parts = (
        profile.role_keywords
        + profile.skills
        + profile.locations
        + ([profile.wants_text] if profile.wants_text else [])
    )
    query = " ".join(parts).strip()
    return query or "job"


class Session:
    def __init__(self):
        self.profile = PreferenceProfile()
        self.history: list[ChatTurn] = []


class Agent:
    def __init__(self, llm, embedder, store, settings: Settings):
        self.llm = llm
        self.embedder = embedder
        self.store = store
        self.settings = settings
        self._sessions: dict[str, Session] = {}
        self._seeded = False

    def ensure_seeded(self) -> None:
        if self._seeded:
            return
        # No-op for the memory store; creates the pgvector schema for
        # Postgres before the first read.
        self.store.init_schema()
        existing = {job.id for job in self.store.list_jobs()}
        for job in SEED_JOBS:
            if job.id not in existing:
                self.store.upsert_job(job, self.embedder.embed(job.search_text()))
        self._seeded = True

    def _extract_patch(self, message: str, session: Session) -> ProfilePatch:
        history = "\n".join(
            f"{turn.role}: {turn.text}" for turn in session.history[-6:]
        )
        prompt = EXTRACT_PROMPT.format(
            profile=session.profile.model_dump_json(),
            history=history or "(no previous turns)",
            message=message,
        )
        try:
            raw = self.llm.generate(prompt, as_json=True)
            return ProfilePatch.model_validate(json.loads(_extract_json(raw)))
        except Exception:
            return extract_profile_rules(message)

    def _compose_reply(
        self, profile: PreferenceProfile, ranked: list[RankedJob], session: Session
    ) -> str:
        jobs_json = json.dumps(
            [item.model_dump(mode="json") for item in ranked], indent=1
        )
        prompt = COMPOSE_PROMPT.format(
            profile=profile.model_dump_json(), jobs_json=jobs_json
        )
        try:
            raw = self.llm.generate(prompt, as_json=True)
            reply = str(json.loads(_extract_json(raw)).get("reply", "")).strip()
            return reply or _template_reply(profile, ranked)
        except Exception:
            return _template_reply(profile, ranked)

    def search_jobs(
        self, args: SearchToolArgs, profile: PreferenceProfile, top_k: int = 5
    ) -> list[RankedJob]:
        """The agent's search_jobs tool: semantic retrieval + reranking."""
        self.ensure_seeded()
        embedding = self.embedder.embed(args.query)
        candidates = self.store.search(embedding, args.top_k)
        return rerank(profile, candidates, top_k=top_k)

    def chat(self, session_id: str | None, message: str, top_k: int = 5) -> ChatResponse:
        self.ensure_seeded()
        session_id = session_id or uuid.uuid4().hex[:12]
        session = self._sessions.setdefault(session_id, Session())

        patch = self._extract_patch(message, session)
        session.profile = merge_patch(session.profile, patch)

        query = build_search_query(session.profile)
        ranked = self.search_jobs(
            SearchToolArgs(query=query, top_k=20),
            session.profile,
            top_k=top_k,
        )
        reply = self._compose_reply(session.profile, ranked, session)

        session.history.append(ChatTurn(role="user", text=message))
        session.history.append(ChatTurn(role="agent", text=reply))
        session.history = session.history[-2 * self.settings.max_history_turns :]

        return ChatResponse(
            reply=reply,
            session_id=session_id,
            jobs=ranked,
            profile=session.profile,
            llm_provider=self.llm.name,
            embedding_provider=self.embedder.name,
            store=self.store.name,
        )


def build_agent(settings: Settings) -> Agent:
    """Build an agent from settings. With no key and no DATABASE_URL
    this is the $0 demo configuration (stub LLM + hash embeddings +
    in-memory store)."""
    embedder = get_embedder(settings)
    llm = get_llm(settings)
    if settings.store == "postgres":
        store = PgVectorStore(settings.database_url, settings.embedding_dim)
    else:
        store = InMemoryStore()
    return Agent(llm, embedder, store, settings)
