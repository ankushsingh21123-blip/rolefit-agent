"""Configuration from the environment.

Secrets come from the environment only and are never written to disk by
this app. ``GEMINI_API_KEY`` unset means demo mode (see llm.py and
embeddings.py): the app still runs end to end with a stub LLM and
hash embeddings, clearly labelled as demo-only.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"
    # Verified live 24 Nov 2026: text-embedding-004 returns 404 for this
    # key ("not found for API version v1beta"); gemini-embedding-001
    # works and returns 3072-dim vectors.
    gemini_embed_model: str = "gemini-embedding-001"
    store: str = "memory"  # "memory" or "postgres"
    database_url: str = ""
    embedding_dim: int = 3072
    max_history_turns: int = 8
    default_top_k: int = 5


def get_settings() -> Settings:
    return Settings(
        gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
        gemini_model=os.environ.get("GEMINI_MODEL", "gemini-3.6-flash"),
        gemini_embed_model=os.environ.get(
            "GEMINI_EMBED_MODEL", "gemini-embedding-001"
        ),
        store=os.environ.get("STORE", "memory"),
        database_url=os.environ.get("DATABASE_URL", ""),
        embedding_dim=int(os.environ.get("EMBEDDING_DIM", "3072")),
        max_history_turns=int(os.environ.get("MAX_HISTORY_TURNS", "8")),
        default_top_k=int(os.environ.get("DEFAULT_TOP_K", "5")),
    )
