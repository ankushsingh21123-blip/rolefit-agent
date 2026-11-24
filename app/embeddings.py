"""Embedding providers.

Two providers, selected by environment (same pattern as the rag-demo):

1. ``GeminiEmbedder`` — real embeddings from the Gemini API
   (gemini-embedding-001, 3072 dims), used only when ``GEMINI_API_KEY``
   is set. The key is read from the environment and never stored in
   this repo. The call is a plain REST POST, the same shape the
   rag-demo uses. NOTE: text-embedding-004 returns 404 for this key
   (verified 24 Nov 2026), so gemini-embedding-001 is the default.
2. ``FallbackEmbedder`` — DEMO ONLY. A deterministic hash-based embedder
   that lets the app and its tests run with $0 and no API keys. It is
   NOT a production embedding model: it captures token overlap only and
   has no semantic understanding. It is labelled demo-only everywhere
   it appears (code, API responses, README) and must never be presented
   as production embeddings.
"""

import hashlib
import math
import re

import httpx

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def hash_embed(text: str, dim: int = 768) -> list[float]:
    """Deterministic hash-based embedding. DEMO ONLY, see module docstring."""
    vector = [0.0] * dim
    for token in _TOKEN_RE.findall(text.lower()):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:8], "big") % dim
        vector[index] += 1.0
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0:
        return vector
    return [v / norm for v in vector]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class FallbackEmbedder:
    """DEMO ONLY embedder. Deterministic, keyless, no semantics."""

    name = "fallback-demo-only"

    def __init__(self, dim: int = 768):
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        return hash_embed(text, self.dim)


class GeminiEmbedder:
    """Real embeddings via the Gemini API (gemini-embedding-001 by default)."""

    name = "gemini"

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-embedding-001",
        client: httpx.Client | None = None,
    ):
        self.api_key = api_key
        self.model = model
        self._client = client

    def embed(self, text: str) -> list[float]:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:embedContent"
        )
        payload = {"content": {"parts": [{"text": text}]}}
        headers = {"x-goog-api-key": self.api_key}
        if self._client is not None:
            response = self._client.post(url, json=payload, headers=headers)
        else:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["embedding"]["values"]


def get_embedder(settings):
    """Return the Gemini embedder when a key is configured, else the
    clearly-labelled demo-only fallback."""
    if settings.gemini_api_key:
        return GeminiEmbedder(settings.gemini_api_key, settings.gemini_embed_model)
    return FallbackEmbedder(settings.embedding_dim)
