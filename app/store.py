"""Vector storage for the jobs index.

``PgVectorStore`` is the real store: Postgres + pgvector, addressed by
``DATABASE_URL`` (same pattern as the rag-demo; works with a local
pgvector container from docker-compose.yml or a Supabase Postgres
project). ``InMemoryStore`` is a dependency-injected stand-in used by
the test suite and by ``STORE=memory`` local runs with no database; it
implements the same interface with in-process cosine similarity.

One embedding per job (its ``search_text``), not per chunk: the index
is small by design and the demo must seed in one step.
"""

from dataclasses import dataclass

from .embeddings import cosine_similarity
from .models import Job


@dataclass
class RetrievedJob:
    job: Job
    score: float


class InMemoryStore:
    """In-memory store for tests and keyless local runs."""

    name = "memory"

    def __init__(self):
        self._jobs: dict[str, Job] = {}
        self._embeddings: dict[str, list[float]] = {}

    def init_schema(self) -> None:
        return None

    def upsert_job(self, job: Job, embedding: list[float]) -> None:
        self._jobs[job.id] = job
        self._embeddings[job.id] = embedding

    def list_jobs(self) -> list[Job]:
        return [self._jobs[job_id] for job_id in sorted(self._jobs)]

    def search(self, query_embedding: list[float], top_k: int) -> list[RetrievedJob]:
        scored = [
            (
                cosine_similarity(query_embedding, emb),
                self._jobs[job_id],
            )
            for job_id, emb in self._embeddings.items()
        ]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            RetrievedJob(job=job, score=score) for score, job in scored[:top_k]
        ]


class PgVectorStore:
    """Postgres + pgvector store. Requires the ``pgvector`` extension."""

    name = "postgres"

    def __init__(self, database_url: str, embedding_dim: int = 768):
        if not database_url:
            raise ValueError("DATABASE_URL is required for the postgres store")
        try:
            import psycopg
        except ImportError as exc:  # pragma: no cover - import guard
            raise RuntimeError(
                "psycopg is required for the postgres store; "
                "install requirements.txt"
            ) from exc
        self._psycopg = psycopg
        self._database_url = database_url
        self._dim = embedding_dim
        self._conn = None

    def _connect(self):
        if self._conn is None or self._conn.closed:
            self._conn = self._psycopg.connect(self._database_url)
        return self._conn

    @staticmethod
    def _vector_literal(embedding: list[float]) -> str:
        return "[" + ",".join(repr(float(v)) for v in embedding) + "]"

    def init_schema(self) -> None:
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT NOT NULL,
                    work_mode TEXT NOT NULL,
                    employment_type TEXT NOT NULL,
                    salary_min INTEGER NOT NULL,
                    salary_max INTEGER NOT NULL,
                    skills TEXT NOT NULL,
                    description TEXT NOT NULL,
                    embedding vector(%s) NOT NULL
                )
                """ % self._dim
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS jobs_embedding_idx
                ON jobs USING ivfflat (embedding vector_cosine_ops)
                """
            )
        conn.commit()

    def upsert_job(self, job: Job, embedding: list[float]) -> None:
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO jobs
                    (id, title, company, location, work_mode,
                     employment_type, salary_min, salary_max, skills,
                     description, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    company = EXCLUDED.company,
                    location = EXCLUDED.location,
                    work_mode = EXCLUDED.work_mode,
                    employment_type = EXCLUDED.employment_type,
                    salary_min = EXCLUDED.salary_min,
                    salary_max = EXCLUDED.salary_max,
                    skills = EXCLUDED.skills,
                    description = EXCLUDED.description,
                    embedding = EXCLUDED.embedding
                """,
                (
                    job.id,
                    job.title,
                    job.company,
                    job.location,
                    job.work_mode,
                    job.employment_type,
                    job.salary_min,
                    job.salary_max,
                    ",".join(job.skills),
                    job.description,
                    self._vector_literal(embedding),
                ),
            )
        conn.commit()

    def list_jobs(self) -> list[Job]:
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, company, location, work_mode,
                       employment_type, salary_min, salary_max, skills,
                       description
                FROM jobs ORDER BY id
                """
            )
            jobs = []
            for row in cur.fetchall():
                (job_id, title, company, location, work_mode,
                 employment_type, salary_min, salary_max, skills,
                 description) = row
                jobs.append(
                    Job(
                        id=job_id,
                        title=title,
                        company=company,
                        location=location,
                        work_mode=work_mode,
                        employment_type=employment_type,
                        salary_min=salary_min,
                        salary_max=salary_max,
                        skills=[s for s in skills.split(",") if s],
                        description=description,
                    )
                )
            return jobs

    def search(self, query_embedding: list[float], top_k: int) -> list[RetrievedJob]:
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, company, location, work_mode,
                       employment_type, salary_min, salary_max, skills,
                       description,
                       1 - (embedding <=> %s::vector) AS score
                FROM jobs
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    self._vector_literal(query_embedding),
                    self._vector_literal(query_embedding),
                    top_k,
                ),
            )
            results = []
            for row in cur.fetchall():
                (job_id, title, company, location, work_mode,
                 employment_type, salary_min, salary_max, skills,
                 description, score) = row
                results.append(
                    RetrievedJob(
                        job=Job(
                            id=job_id,
                            title=title,
                            company=company,
                            location=location,
                            work_mode=work_mode,
                            employment_type=employment_type,
                            salary_min=salary_min,
                            salary_max=salary_max,
                            skills=[s for s in skills.split(",") if s],
                            description=description,
                        ),
                        score=float(score),
                    )
                )
            return results

    def close(self) -> None:
        if self._conn is not None and not self._conn.closed:
            self._conn.close()
        self._conn = None
