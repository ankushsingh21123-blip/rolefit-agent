"""Shared fixtures: a stub-LLM agent over the in-memory store."""

import pytest

from app.agent import build_agent
from app.config import Settings


@pytest.fixture
def agent():
    settings = Settings()  # no key -> stub LLM + hash embeddings + memory
    ag = build_agent(settings)
    ag.ensure_seeded()
    return ag
