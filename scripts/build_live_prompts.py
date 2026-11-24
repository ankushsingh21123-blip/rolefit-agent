"""Build the exact prompts the agent sends to Gemini, for live checking.

Runs one chat turn through the agent with a recording stub LLM, then
writes the two prompts (extract + compose) to /tmp files. Those files
are then sent to the real Gemini API via the registered custom.gemini
connector helper, which holds the key. No key is read or printed here.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import Agent
from app.config import Settings
from app.embeddings import FallbackEmbedder
from app.llm import StubLLMClient
from app.store import InMemoryStore


class RecordingLLM(StubLLMClient):
    def __init__(self):
        self.prompts: list[str] = []

    def generate(self, prompt: str, as_json: bool = False) -> str:
        self.prompts.append(prompt)
        return super().generate(prompt, as_json=as_json)


def main() -> int:
    llm = RecordingLLM()
    agent = Agent(llm, FallbackEmbedder(), InMemoryStore(), Settings())
    response = agent.chat(
        "live",
        "I want a remote Python backend job, at least ₹40,000 a month. "
        "I never want night shifts.",
    )
    print("stub top jobs:", [j.job.id for j in response.jobs[:3]])
    with open("/tmp/rolefit_extract_prompt.txt", "w") as f:
        f.write(llm.prompts[0])
    with open("/tmp/rolefit_compose_prompt.txt", "w") as f:
        f.write(llm.prompts[1])
    print("wrote /tmp/rolefit_extract_prompt.txt and /tmp/rolefit_compose_prompt.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
