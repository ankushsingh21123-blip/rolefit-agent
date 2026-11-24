"""Agent: multi-turn memory, tool use, structured replies."""

from app.agent import build_search_query, merge_patch
from app.models import PreferenceProfile, ProfilePatch


def test_chat_returns_ranked_jobs_with_reasons(agent):
    response = agent.chat(
        "s1", "I want a remote Python backend job, at least ₹40,000 a month."
    )
    assert response.session_id == "s1"
    assert response.jobs, "expected at least one match"
    assert response.jobs[0].job.id == "job-08"
    assert response.jobs[0].reasons
    assert "job-08" in response.reply or "Nimbus Cloud" in response.reply
    assert response.llm_provider == "stub-demo-only"
    assert response.embedding_provider == "fallback-demo-only"


def test_chat_remembers_context_across_turns(agent):
    first = agent.chat("s2", "I want a React job in Hyderabad.")
    assert "Hyderabad" in first.profile.locations
    assert "React" in first.profile.skills
    second = agent.chat("s2", "Actually, make it part-time and remote if possible.")
    assert "Hyderabad" in second.profile.locations  # remembered
    assert "React" in second.profile.skills  # remembered
    assert "Part-time" in second.profile.employment_types  # new
    assert second.jobs and second.jobs[0].job.id == "job-21"


def test_chat_respects_deal_breakers(agent):
    response = agent.chat(
        "s3", "I want a job in Hyderabad. I never want sales or customer support calls."
    )
    top_ids = [item.job.id for item in response.jobs[:3]]
    assert "job-13" not in top_ids
    assert "job-14" not in top_ids
    assert "job-29" not in top_ids


def test_chat_honest_when_nothing_matches(agent):
    response = agent.chat(
        "s4", "I want a part-time astronaut job on the Moon, at least ₹2,00,000 a month."
    )
    assert response.jobs == []
    assert "couldn't find" in response.reply.lower()


def test_merge_patch_unions_lists():
    profile = PreferenceProfile(skills=["Python"], locations=["Bengaluru"])
    patch = ProfilePatch(skills=["SQL"], locations=["Hyderabad"], min_salary_monthly=30000)
    merged = merge_patch(profile, patch)
    assert merged.skills == ["Python", "SQL"]
    assert merged.locations == ["Bengaluru", "Hyderabad"]
    assert merged.min_salary_monthly == 30000


def test_build_search_query_uses_profile():
    profile = PreferenceProfile(
        role_keywords=["backend"], skills=["Python"], locations=["Remote"]
    )
    query = build_search_query(profile)
    assert "backend" in query and "Python" in query and "Remote" in query
    assert build_search_query(PreferenceProfile()) == "job"


def test_sessions_are_isolated(agent):
    agent.chat("a", "I want a React job in Hyderabad.")
    other = agent.chat("b", "I want a design internship.")
    assert "Hyderabad" not in other.profile.locations
    assert "React" not in other.profile.skills
