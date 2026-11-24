"""Data models for RoleFit Agent.

Everything the agent passes around is a typed Pydantic model so the
LLM's structured outputs can be validated instead of trusted blindly.
"""

from pydantic import BaseModel, Field


class Job(BaseModel):
    """One job listing. All seeded listings are fictional (see seed_jobs)."""

    id: str
    title: str
    company: str
    location: str  # city, or "Remote"
    work_mode: str  # "Remote" | "On-site" | "Hybrid"
    employment_type: str  # "Full-time" | "Part-time" | "Internship"
    salary_min: int  # monthly INR
    salary_max: int  # monthly INR
    skills: list[str] = Field(default_factory=list)
    description: str = ""

    def search_text(self) -> str:
        """Text embedded for semantic search."""
        return (
            f"{self.title} at {self.company}. {self.description} "
            f"Location: {self.location}. Mode: {self.work_mode}. "
            f"Type: {self.employment_type}. "
            f"Salary: {self.salary_min}-{self.salary_max} INR per month. "
            f"Skills: {', '.join(self.skills)}."
        )


class PreferenceProfile(BaseModel):
    """What the agent has learned about a person so far. Built up turn
    by turn and remembered across the conversation."""

    wants_text: str = ""
    role_keywords: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    min_salary_monthly: int | None = None
    employment_types: list[str] = Field(default_factory=list)
    work_modes: list[str] = Field(default_factory=list)
    never: list[str] = Field(default_factory=list)  # deal-breakers
    notes: list[str] = Field(default_factory=list)


class ProfilePatch(BaseModel):
    """Structured output of the extraction step. Only the fields the
    person actually stated are filled; the rest stay null/empty."""

    wants_text: str | None = None
    role_keywords: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    min_salary_monthly: int | None = None
    employment_types: list[str] = Field(default_factory=list)
    work_modes: list[str] = Field(default_factory=list)
    never: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ChatTurn(BaseModel):
    role: str  # "user" | "agent"
    text: str


class RankedJob(BaseModel):
    job: Job
    score: float
    reasons: list[str] = Field(default_factory=list)


class SearchToolArgs(BaseModel):
    """What the agent passes to its search_jobs tool (structured output)."""

    query: str
    top_k: int = 20


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=10)


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    jobs: list[RankedJob] = Field(default_factory=list)
    profile: PreferenceProfile
    llm_provider: str
    embedding_provider: str
    store: str


class EvalCaseResult(BaseModel):
    case_id: str
    hit_at_3: bool
    reciprocal_rank: float
    violations: list[str] = Field(default_factory=list)
    top_job_ids: list[str] = Field(default_factory=list)


class EvalReport(BaseModel):
    cases: list[EvalCaseResult]
    hit_at_3: float
    mrr_at_5: float
    violation_count: int
    llm_provider: str
    embedding_provider: str
