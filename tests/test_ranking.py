"""Ranking: deal-breakers are hard filters, scores are explainable."""

from app.models import Job, PreferenceProfile
from app.ranking import rerank, score_job, violates_deal_breaker
from app.store import RetrievedJob


def _job(**overrides):
    base = dict(
        id="job-x",
        title="Backend Engineer",
        company="Test Co",
        location="Bengaluru",
        work_mode="Hybrid",
        employment_type="Full-time",
        salary_min=50000,
        salary_max=80000,
        skills=["Python", "SQL"],
        description="Python backend work with SQL.",
    )
    base.update(overrides)
    return Job(**base)


def test_never_sales_excludes_sales_job():
    profile = PreferenceProfile(never=["sales"])
    sales = _job(id="job-s", title="Sales Executive", skills=["Sales"])
    assert violates_deal_breaker(profile, sales) is not None
    backend = _job()
    assert violates_deal_breaker(profile, backend) is None


def test_never_night_shift_excludes_night_job():
    profile = PreferenceProfile(never=["night shift"])
    night = _job(
        id="job-n",
        title="Support Engineer",
        description="Night-shift support, 10 PM to 6 AM.",
    )
    assert violates_deal_breaker(profile, night) is not None


def test_salary_floor_excludes_low_pay():
    profile = PreferenceProfile(min_salary_monthly=60000)
    low = _job(salary_min=20000, salary_max=30000)
    assert violates_deal_breaker(profile, low) is not None
    ok = _job(salary_min=55000, salary_max=80000)
    assert violates_deal_breaker(profile, ok) is None


def test_location_filter_allows_remote_jobs():
    profile = PreferenceProfile(locations=["Bengaluru"])
    remote = _job(location="Remote", work_mode="Remote")
    assert violates_deal_breaker(profile, remote) is None
    mumbai = _job(location="Mumbai", work_mode="On-site")
    assert violates_deal_breaker(profile, mumbai) is not None


def test_remote_only_location_excludes_onsite():
    profile = PreferenceProfile(locations=["Remote"])
    onsite = _job(location="Bengaluru", work_mode="On-site")
    assert violates_deal_breaker(profile, onsite) is not None


def test_employment_type_is_a_hard_filter():
    profile = PreferenceProfile(employment_types=["Part-time"])
    full = _job(employment_type="Full-time")
    assert violates_deal_breaker(profile, full) is not None


def test_work_mode_is_soft_not_a_hard_filter():
    # A hybrid role in the person's city is still shown when they asked
    # for remote; it just scores lower than a remote one.
    profile = PreferenceProfile(locations=["Bengaluru"], work_modes=["Remote"])
    hybrid = _job(location="Bengaluru", work_mode="Hybrid")
    assert violates_deal_breaker(profile, hybrid) is None
    remote = _job(location="Remote", work_mode="Remote")
    s_hybrid, _ = score_job(profile, hybrid, 0.5)
    s_remote, _ = score_job(profile, remote, 0.5)
    assert s_remote > s_hybrid


def test_score_explains_itself():
    profile = PreferenceProfile(
        skills=["Python", "SQL"],
        locations=["Bengaluru"],
        min_salary_monthly=40000,
    )
    score, reasons = score_job(profile, _job(), 0.6)
    assert 0.0 <= score <= 1.0
    assert any("Python" in r for r in reasons)
    assert any("Bengaluru" in r for r in reasons)
    assert any("40,000" in r for r in reasons)


def test_rerank_orders_and_limits(agent):
    profile = PreferenceProfile(skills=["Python"], locations=["Remote"])
    candidates = agent.store.search(agent.embedder.embed("python backend"), 20)
    ranked = rerank(profile, candidates, top_k=3)
    assert len(ranked) == 3
    scores = [r.score for r in ranked]
    assert scores == sorted(scores, reverse=True)
    assert all("Python" in r.job.skills or r.score >= 0 for r in ranked)
