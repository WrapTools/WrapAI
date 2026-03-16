# ai_helper.py
"""
WrapAI helper — reusable functions built on open_provider.
Mirrors the WrapEmbed helper pattern.

Usage:
    from WrapAI.ai_helper import send, stream, make_ai, set_defaults

    # No args — uses Venice defaults
    send("What is the capital of France?")

    # Provider only — uses that provider's own defaults
    send("What is the capital of France?", provider="OpenAI")

    # Explicit — provider required if model or api_key are passed
    send("What is the capital of France?", provider="OpenAI", model="gpt-4o", api_key="OPENAI_API_KEY")

    # Override module defaults once at top of script
    set_defaults(provider="OpenAI", model="gpt-4o-mini", api_key="OPENAI_API_KEY")
"""

from WrapAI import open_provider, inspect

# ---------------------------------------------------------------------------
# Module-level defaults
# ---------------------------------------------------------------------------

_DEFAULT_PROVIDER = "Venice"

_PROVIDER_DEFAULTS = {
    "Venice": {"model": "llama-3.3-70b",  "api_key": "VENICE_API_KEY"},
    "OpenAI": {"model": "gpt-4o-mini",    "api_key": "OPENAI_API_KEY"},
}


def set_defaults(provider: str = None, model: str = None, api_key: str = None) -> None:
    """
    Override module-level defaults for all helper functions.
    Only overrides values that are explicitly passed.

    Example:
        set_defaults(provider="OpenAI", model="gpt-4o-mini", api_key="OPENAI_API_KEY")
    """
    global _DEFAULT_PROVIDER
    if provider is not None:
        if provider not in _PROVIDER_DEFAULTS:
            raise ValueError(f"Unknown provider '{provider}'. Choose from: {list(_PROVIDER_DEFAULTS)}")
        _DEFAULT_PROVIDER = provider
    if model is not None:
        _PROVIDER_DEFAULTS[_DEFAULT_PROVIDER]["model"] = model
    if api_key is not None:
        _PROVIDER_DEFAULTS[_DEFAULT_PROVIDER]["api_key"] = api_key


def _resolve(provider, model, api_key):
    """Resolve provider/model/api_key using defaults where not supplied."""
    if model is not None or api_key is not None:
        if provider is None:
            raise ValueError(
                "provider must be specified when passing model or api_key."
            )
    p = provider or _DEFAULT_PROVIDER
    if p not in _PROVIDER_DEFAULTS:
        raise ValueError(f"Unknown provider '{p}'. Choose from: {list(_PROVIDER_DEFAULTS)}")
    defaults = _PROVIDER_DEFAULTS[p]
    return p, model or defaults["model"], api_key or defaults["api_key"]


# ---------------------------------------------------------------------------
# Provider setup
# ---------------------------------------------------------------------------

def make_ai(provider=None, model=None, api_key=None, **options):
    """Create and configure an ai object. Pass any set_options kwargs directly."""
    p, m, k = _resolve(provider, model, api_key)
    ai = open_provider(provider=p, model=m, api_key=k)
    if options:
        ai.set_options(**options)
    return ai


# ---------------------------------------------------------------------------
# Stateless text
# ---------------------------------------------------------------------------

def send(prompt_text, provider=None, model=None, api_key=None, **options):
    """Single-turn stateless send. Returns response string."""
    ai = make_ai(provider=provider, model=model, api_key=api_key, **options)
    return ai.send_text_prompt(prompt_text)


def stream(prompt_text, provider=None, model=None, api_key=None, **options):
    """Single-turn stateless stream. Prints chunks inline."""
    ai = make_ai(provider=provider, model=model, api_key=api_key, **options)
    for chunk in ai.stream_text_prompt(prompt_text):
        print(chunk, end="", flush=True)
    print()


# ---------------------------------------------------------------------------
# Stateful chat (caller holds the ai object for memory persistence)
# ---------------------------------------------------------------------------

def chat(ai, message):
    """Send a message to a stateful ai object. Returns response string."""
    return ai.send_chat_prompt(message)


def stream_chat(ai, message):
    """Stream a message to a stateful ai object. Prints chunks inline."""
    for chunk in ai.stream_chat_prompt(message):
        print(chunk, end="", flush=True)
    print()


# ---------------------------------------------------------------------------
# Library-based prompts
# ---------------------------------------------------------------------------

def send_from_library(library_path, key, values=None, provider=None, model=None, api_key=None):
    """Load a library and send a named prompt. Stateless."""
    ai = make_ai(provider=provider, model=model, api_key=api_key)
    ai.load_library(library_path)
    return ai.send_text_prompt_from_library(key=key, values=values)


# ---------------------------------------------------------------------------
# Inspect helpers (stateless — no ai object needed)
# ---------------------------------------------------------------------------

def list_models(provider=None, api_key=None):
    """Return list of available models for a provider."""
    p, _, k = _resolve(provider, None, api_key)
    return inspect.list_models(provider=p, api_key=k)


def count_tokens(text):
    """Return token count for a string."""
    return inspect.count_tokens(text)


def preview_prompt(library_path, key):
    """Preview a prompt from a library without sending."""
    library = inspect.load_library(library_path)
    return inspect.preview_prompt(library, key)
