"""LLM clients.

Two clients behind one interface:

1. ``GeminiClient`` — real calls to the Gemini API over plain REST
   (``generateContent``), the same shape the registered custom.gemini
   connector helper uses. Used only when ``GEMINI_API_KEY`` is set.
   The key is read from the environment and never logged.
2. ``StubLLMClient`` — DEMO ONLY. Deterministic, keyless, rule-based:
   profile extraction uses the rules in extract.py and replies are
   templated from the ranked jobs. It is labelled demo-only everywhere
   it appears and must never be presented as a real LLM.
"""

import json
import re

import httpx

from .extract import extract_profile_rules


class GeminiClient:
    """Real LLM calls via the Gemini REST API."""

    name = "gemini"

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-3.6-flash",
        client: httpx.Client | None = None,
    ):
        self.api_key = api_key
        self.model = model
        self._client = client

    def generate(self, prompt: str, as_json: bool = False) -> str:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        generation_config: dict = {"temperature": 0.2}
        if as_json:
            generation_config["responseMimeType"] = "application/json"
        payload = {
            "generationConfig": generation_config,
            "contents": [{"parts": [{"text": prompt}]}],
        }
        headers = {"x-goog-api-key": self.api_key}
        if self._client is not None:
            response = self._client.post(url, json=payload, headers=headers)
        else:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        candidates = data.get("candidates") or []
        if not candidates:
            raise ValueError(
                "Gemini returned no candidates: "
                + json.dumps(data.get("promptFeedback", {}))
            )
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts).strip()
        if not text:
            raise ValueError("Gemini returned an empty reply")
        return text


class StubLLMClient:
    """DEMO ONLY LLM. Deterministic, keyless, rule-based."""

    name = "stub-demo-only"

    def generate(self, prompt: str, as_json: bool = False) -> str:
        if "TASK: EXTRACT_PROFILE" in prompt:
            match = re.search(
                r"USER MESSAGE:\n(.*?)\nEND MESSAGE", prompt, re.DOTALL
            )
            message = match.group(1).strip() if match else ""
            patch = extract_profile_rules(message)
            return json.dumps(patch.model_dump())
        if "TASK: COMPOSE_REPLY" in prompt:
            match = re.search(r"JOBS_JSON:\n(.*?)\nEND JOBS_JSON", prompt, re.DOTALL)
            jobs = json.loads(match.group(1)) if match else []
            lines = []
            if jobs:
                lines.append(
                    "Here are the closest matches I found for you:"
                )
                for job in jobs:
                    reason = (job.get("reasons") or ["Good match"])[0]
                    lines.append(
                        f"- {job['job']['title']} at {job['job']['company']} — "
                        f"{job['job']['location']}, {job['job']['work_mode']}, "
                        f"{job['job']['employment_type']}, "
                        f"₹{job['job']['salary_min']:,}–₹{job['job']['salary_max']:,} a month. "
                        f"{reason}."
                    )
                lines.append(
                    "Want me to narrow this down? Tell me what to change — "
                    "role, place, pay, or something you'd never take."
                )
            else:
                lines.append(
                    "I couldn't find a match for that yet in the jobs I "
                    "know about. Could you tell me a bit more — for "
                    "example the role, the place, or the minimum pay "
                    "you'd accept?"
                )
            return json.dumps({"reply": "\n".join(lines)})
        return json.dumps({})


def get_llm(settings):
    """Return the Gemini client when a key is configured, else the
    clearly-labelled demo-only stub."""
    if settings.gemini_api_key:
        return GeminiClient(settings.gemini_api_key, settings.gemini_model)
    return StubLLMClient()
