"""Stores and embeddings: the plumbing the agent stands on."""

from app.embeddings import FallbackEmbedder, cosine_similarity, hash_embed
from app.models import Job
from app.store import InMemoryStore


def _job(job_id="job-t"):
    return Job(
        id=job_id,
        title="Python Developer",
        company="Test Co",
        location="Remote",
        work_mode="Remote",
        employment_type="Full-time",
        salary_min=50000,
        salary_max=70000,
        skills=["Python"],
        description="Python work, remote.",
    )


def test_hash_embed_is_deterministic():
    a = hash_embed("python backend remote")
    b = hash_embed("python backend remote")
    assert a == b
    c = hash_embed("design figma internship")
    assert a != c
    assert abs(sum(v * v for v in a) - 1.0) < 1e-6  # unit norm


def test_cosine_similarity_basics():
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0
    assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0


def test_fallback_embedder_name():
    embedder = FallbackEmbedder()
    assert embedder.name == "fallback-demo-only"
    assert len(embedder.embed("hello")) == 768


def test_memory_store_upsert_and_search():
    store = InMemoryStore()
    store.init_schema()
    embedder = FallbackEmbedder()
    job = _job()
    store.upsert_job(job, embedder.embed(job.search_text()))
    assert len(store.list_jobs()) == 1
    results = store.search(embedder.embed("python developer remote"), 5)
    assert len(results) == 1
    assert results[0].job.id == "job-t"
    assert results[0].score > 0.5


def test_memory_store_upsert_overwrites():
    store = InMemoryStore()
    embedder = FallbackEmbedder()
    store.upsert_job(_job(), embedder.embed("a"))
    store.upsert_job(_job(), embedder.embed("b"))
    assert len(store.list_jobs()) == 1
