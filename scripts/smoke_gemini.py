"""One live Gemini round-trip: embedding + a structured chat turn.

Reads GEMINI_API_KEY from the environment. Prints only the results,
never the key. Exits 2 (skip) if no key is set, non-zero if the call
fails. Used to prove the real LLM path works before pushing.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import build_agent
from app.config import get_settings


def main() -> int:
    settings = get_settings()
    if not settings.gemini_api_key:
        print("SKIP: GEMINI_API_KEY is not set in this environment.")
        return 2
    agent = build_agent(settings)
    agent.ensure_seeded()
    print(
        "providers:",
        agent.llm.name,
        "+",
        agent.embedder.name,
        "+",
        agent.store.name,
    )
    resp = agent.chat(
        "smoke",
        "I want a remote Python backend job, at least ₹40,000 a month. "
        "I never want night shifts.",
    )
    print("top jobs:", [(j.job.id, round(j.score, 3)) for j in resp.jobs[:3]])
    print("reply:")
    print(resp.reply[:800])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
