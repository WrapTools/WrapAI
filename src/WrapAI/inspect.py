# wrapai/inspect.py
"""
WrapAI inspect — stateless diagnostics. No side effects, no memory.

Usage:
    from wrapai import inspect

    models = inspect.list_models(provider="Venice", api_key="VENICE_API_KEY")
    tokens = inspect.count_tokens("Hello world")
    lib    = inspect.load_library("prompts/my_prompts.json")
    names  = inspect.list_prompts(lib)
"""

import os
from typing import Any, Optional

from WrapAI import ModelRegistry
from WrapAI.info.account_info import VeniceApiKeyInfo
from WrapAI.utils.tokens_char import count_characters_and_tokens, split_text_to_token_chunks
from WrapAI.core.prompt_library import PromptLibrary
from WrapAI.core.wv_core import PROVIDER_VENICE, PROVIDER_OPENAI
from WrapAI.utils.secret_loader import load_secret


def _resolve_key(api_key: str) -> str:
    """Resolve env-var name or raw key string via .env file."""
    return load_secret(api_key)


# ---------------------------------------------------------------------------
# Model inspection
# ---------------------------------------------------------------------------

def list_models(provider: str, api_key: str) -> list[str]:
    """
    Return a list of model ID strings for the given provider.

    Args:
        provider: "Venice" or "OpenAI"
        api_key:  Raw key string or env-var name
    """
    key = _resolve_key(api_key)
    registry = ModelRegistry(provider=provider, api_key=key)
    registry.fetch_models()
    return registry.list_models()


def get_model_details(provider: str, api_key: str, model_id: str) -> dict[str, Any]:
    """Return the full spec dict for a single model."""
    key = _resolve_key(api_key)
    registry = ModelRegistry(provider=provider, api_key=key)
    registry.fetch_models()
    return registry.get_model_details(model_id)


def get_all_models(provider: str, api_key: str) -> dict[str, Any]:
    """Return a dict of all models keyed by model ID."""
    key = _resolve_key(api_key)
    registry = ModelRegistry(provider=provider, api_key=key)
    registry.fetch_models()
    return registry.get_all()


def filter_models(
    provider: str,
    api_key: str,
    capability: str,
) -> list[dict[str, Any]]:
    """
    Return models filtered by a capability flag.

    Venice capability examples:
        "supportsReasoning", "supportsResponseSchema", "supportsFunctionCalling"
    """
    key = _resolve_key(api_key)
    registry = ModelRegistry(provider=provider, api_key=key)
    registry.fetch_models()
    return registry.registry.filter_by_capability(capability)


# ---------------------------------------------------------------------------
# Account info — Venice only
# ---------------------------------------------------------------------------

def account_info(api_key: str) -> dict[str, Any]:
    """
    Venice only — return API key info and rate limits.

    Returns dict with keys: "api_keys", "key_rate_limits", "model_rate_limits"
    """
    key = _resolve_key(api_key)
    info = VeniceApiKeyInfo(api_key=key)

    result: dict[str, Any] = {}

    try:
        result["api_keys"] = info.list_api_keys().json()
    except Exception as e:
        result["api_keys"] = {"error": str(e)}

    try:
        result["key_rate_limits"] = info.list_api_key_rate_limits().json()
    except Exception as e:
        result["key_rate_limits"] = {"error": str(e)}

    try:
        result["model_rate_limits"] = info.get_model_rate_limits().json()
    except Exception as e:
        result["model_rate_limits"] = {"error": str(e)}

    return result


# ---------------------------------------------------------------------------
# Token utilities
# ---------------------------------------------------------------------------

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Return the token count for a string."""
    _, token_count = count_characters_and_tokens(text, model=model)
    return token_count


def count_characters(text: str, model: str = "gpt-3.5-turbo") -> tuple[int, int]:
    """Return (character_count, token_count) for a string."""
    return count_characters_and_tokens(text, model=model)


def split_to_chunks(
    text: str,
    max_tokens: int,
    model: str = "gpt-3.5-turbo",
) -> list[str]:
    """Split text into chunks each no larger than max_tokens."""
    return split_text_to_token_chunks(text, max_tokens=max_tokens, model=model)


# ---------------------------------------------------------------------------
# Prompt library — stateless inspection only
# ---------------------------------------------------------------------------

def load_library(path: str) -> PromptLibrary:
    """Load a prompt library from a JSON file. Returns a PromptLibrary object."""
    return PromptLibrary.from_json_file(path)


def list_prompts(library: PromptLibrary) -> list[str]:
    """Return all prompt names in a loaded library."""
    return library.list_prompts()


def preview_prompt(library: PromptLibrary, key: str) -> Optional[str]:
    """
    Return the raw prompt text for a named prompt without sending it.
    Returns None if the key is not found.
    """
    template = library.get_prompt(key)
    if template is None:
        return None
    return template.get_display_prompt()

