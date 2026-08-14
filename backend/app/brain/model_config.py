"""
Ultron Model Configuration (Phase 2)

Resolves the model IDs for each AI provider from three sources, in priority order:
  1. Environment variable override (e.g. GEMINI_CHAT_MODEL)
  2. config.yaml  ai.models.<provider>
  3. A hard-coded, currently-valid default

This makes the brain provider-agnostic and future-proof: when a provider
retires a model (as Gemini 1.5 / text-embedding-004 already were), switching is
a config change, not a code edit.
"""

import os
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"

# Currently-valid, long-runway defaults (verified against provider docs 2026-08-14):
#   - gemini-3.5-flash    : stable flagship flash, valid to ~May 2027
#   - gemini-embedding-001: stable embeddings, flexible dims, valid to >=May 2028
_DEFAULTS = {
    "groq": "llama-3.1-8b-instant",
    "gemini": "gemini-3.5-flash",
    "nvidia": "nvidia/nvidia/nemotron-3-ultra-550b-a55b",
    "embedding": "gemini-embedding-001",
    "embedding_dims": 768,
}

# env var name per provider (embedding uses the gemini API key too).
_ENV_MAP = {
    "groq": "GROQ_CHAT_MODEL",
    "gemini": "GEMINI_CHAT_MODEL",
    "nvidia": "NVIDIA_CHAT_MODEL",
    "embedding": "GEMINI_EMBEDDING_MODEL",
}


def _load_ai_config() -> dict:
    """Loads the `ai:` block from config.yaml safely (never raises)."""
    if not CONFIG_PATH.exists():
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        return cfg.get("ai", {}) or {}
    except Exception:
        return {}


def get_model(provider: str) -> str:
    """Resolve the chat/embedding model ID for a provider."""
    provider = provider.lower()
    env_name = _ENV_MAP.get(provider)
    if env_name:
        val = os.getenv(env_name)
        if val and val.strip():
            return val.strip()

    models = _load_ai_config().get("models", {}) or {}
    cfg_val = models.get(provider)
    if cfg_val and str(cfg_val).strip():
        return str(cfg_val).strip()

    return _DEFAULTS.get(provider, _DEFAULTS["groq"])


def get_embedding_dimensions() -> int:
    """Resolve the embedding vector dimensionality (must match stored vectors)."""
    env_val = os.getenv("GEMINI_EMBEDDING_DIMS")
    if env_val and env_val.strip().isdigit():
        return int(env_val.strip())

    dims = _load_ai_config().get("embedding_dimensions")
    if dims is not None and str(dims).strip().isdigit():
        return int(str(dims).strip())

    return int(_DEFAULTS["embedding_dims"])
