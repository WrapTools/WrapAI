# wrapai/open_provider.py
"""
WrapAI — top-level entry point.

Usage:
    from wrapai import open_provider
    ai = open_provider(provider="venice", model="llama-3.3-70b", api_key="VENICE_API_KEY")
    ai.set_options(temperature=0.7, venice_options={"enable_web_search": "on"})
    response = ai.send_text_prompt("Explain quantum entanglement.")
    print(response)
"""

import logging
from collections.abc import Iterator
from typing import Optional, Any

from WrapAI.core.provider_config import ProviderConfig
from WrapAI.core.wv_core import PROVIDER_VENICE, PROVIDER_OPENAI
from WrapAI.utils.secret_loader import load_secret
from WrapAI.prompt.prompt_text import VeniceTextPrompt, OpenAITextPrompt
from WrapAI.prompt.prompt_chat import VeniceChatPrompt, OpenAIChatPrompt
from WrapAI.core.prompt_library import PromptLibrary
from WrapAI.core.prompt_attributes import VeniceParameters

logger = logging.getLogger(__name__)

_SUPPORTED_PROVIDERS = (PROVIDER_VENICE, PROVIDER_OPENAI)


def open_provider(
    provider: str,
    model: str,
    api_key: str,
) -> "AIClient":
    """
    Configure a provider and return an AIClient (the `ai` object).

    Args:
        provider:  "venice" or "openai"
        model:     Model name string (e.g. "llama-3.3-70b", "gpt-4o")
        api_key:   Raw key string or env-var / secret name passed to load_secret()

    Returns:
        AIClient instance ready to use.
    """
    if provider not in _SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unsupported provider '{provider}'. Choose from: {_SUPPORTED_PROVIDERS}"
        )

    resolved_key = load_secret(api_key)

    config = ProviderConfig(
        name=provider,
        api_key=resolved_key,
        default_model=model,
        current_model=model,
    )

    return AIClient(config=config, provider=provider)


# ---------------------------------------------------------------------------
# AIClient — the `ai` object returned by open_provider()
# ---------------------------------------------------------------------------

class AIClient:
    """
    Unified AI client wrapping the base prompt modules.

    Instantiated via open_provider() — do not construct directly.
    """

    def __init__(self, config: ProviderConfig, provider: str) -> None:
        self._config = config
        self._provider = provider
        self._system_prompt: str = "You are a helpful assistant."

        # Stateless text runner — always available
        if provider == PROVIDER_VENICE:
            self._text_runner: VeniceTextPrompt | OpenAITextPrompt = VeniceTextPrompt(config)
        else:
            self._text_runner = OpenAITextPrompt(config)

        # Stateful chat runner — lazy init (requires model token lookup)
        self._chat_runner: Optional[VeniceChatPrompt | OpenAIChatPrompt] = None

        # Prompt library — loaded on demand
        self._library: Optional[PromptLibrary] = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_chat_runner(self) -> VeniceChatPrompt | OpenAIChatPrompt:
        """Lazy-init the stateful chat runner."""
        if self._chat_runner is None:
            if self._provider == PROVIDER_VENICE:
                self._chat_runner = VeniceChatPrompt(
                    self._config,
                    system_prompt=self._system_prompt,
                )
            else:
                self._chat_runner = OpenAIChatPrompt(
                    self._config,
                    system_prompt=self._system_prompt,
                )
        return self._chat_runner

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_options(self, **kwargs) -> None:
        """
        Set prompt attributes on both text and chat runners.

        Venice-specific params go in venice_options={} kwarg:
            ai.set_options(temperature=0.7, venice_options={"enable_web_search": "on"})
        """
        venice_options: dict = kwargs.pop("venice_options", {})
        attrs = dict(kwargs)

        if venice_options and self._provider == PROVIDER_VENICE:
            attrs["venice_parameters"] = VeniceParameters(**venice_options)

        if attrs:
            self._text_runner.set_attributes(**attrs)

        if self._chat_runner is not None and attrs:
            self._chat_runner.set_attributes(**attrs)

    def set_system_prompt(self, text: str) -> None:
        """Update the system prompt used for all subsequent requests."""
        self._system_prompt = text
        self._text_runner.last_system_prompt = text  # advisory — used on next call

        if self._chat_runner is not None:
            self._chat_runner.memory.update_system_prompt(text)

    # ------------------------------------------------------------------
    # Stateless — send_text_prompt / stream_text_prompt
    # ------------------------------------------------------------------

    def send_text_prompt(self, text: str) -> str:
        """
        Stateless single-turn prompt. Returns response text.
        No memory — each call is independent.
        """
        result = self._text_runner.prompt(
            user_prompt=text,
            system_prompt=self._system_prompt,
        )
        if result is None:
            raise RuntimeError(
                f"send_text_prompt failed — the API returned no response. "
                f"Check your model ('{self._config.current_model}') supports the "
                f"attributes set via set_options(): "
                f"{self._text_runner.attributes.to_dict(skip_none=True)}"
            )
        return result.response  # removed redundant `if result else ""`

    def stream_text_prompt(self, text: str) -> Iterator[str]:
        """
        Stateless streaming generator. Yields text delta chunks.
        No memory — each call is independent.
        """
        result = self._text_runner.prompt_stream(
            user_prompt=text,
            system_prompt=self._system_prompt,
        )
        if result is None:
            raise RuntimeError(
                f"stream_text_prompt failed — the API returned no response. "
                f"Check your model ('{self._config.current_model}') supports the "
                f"attributes set via set_options(): "
                f"{self._text_runner.attributes.to_dict(skip_none=True)}"
            )
        yield from result

    # ------------------------------------------------------------------
    # Stateful — send_chat_prompt / stream_chat_prompt
    # ------------------------------------------------------------------

    def send_chat_prompt(self, text: str) -> str:
        """
        Stateful multi-turn prompt. Memory is automatic.
        Returns response text.
        """
        chat = self._get_chat_runner()
        result = chat.prompt(user_prompt=text, system_prompt=self._system_prompt)
        if result is None:
            raise RuntimeError(
                f"send_chat_prompt failed — the API returned no response. "
                f"Check your model ('{self._config.current_model}') supports the "
                f"attributes set via set_options(): "
                f"{self._text_runner.attributes.to_dict(skip_none=True)}"
            )
        return result.response

    def stream_chat_prompt(self, text: str) -> Iterator[str]:
        """
        Stateful streaming generator. Memory is automatic.
        Yields text delta chunks and appends the full response to memory.
        """
        chat = self._get_chat_runner()

        # Add user turn to memory before streaming
        chat.memory.add_message("user", text)

        chunks: list[str] = []
        for chunk in self._text_runner.prompt_stream(
                user_prompt=text,
                system_prompt=self._system_prompt,
                messages=chat.memory.message_history,
        ):
            chunks.append(chunk)
            yield chunk

        # Commit assistant reply to memory after stream completes
        full_reply = "".join(chunks)
        if full_reply:
            chat.memory.add_message("assistant", full_reply)

    # ------------------------------------------------------------------
    # Memory management
    # ------------------------------------------------------------------

    def clear_chat_memory(self) -> None:
        """Reset the conversation memory."""
        if self._chat_runner is not None:
            self._chat_runner.clear_memory()

    def summarize_chat_memory(self) -> Optional[str]:
        """
        Compress memory via summarization and keep recent context.
        Returns the summary string.
        """
        chat = self._get_chat_runner()
        summary = chat.summarize_memory()
        if summary:
            chat.memory.reset_with_summary(summary)
        return summary

    # ------------------------------------------------------------------
    # Prompt library
    # ------------------------------------------------------------------

    def load_library(self, path: str) -> None:
        """Attach a prompt library from a JSON file path."""
        self._library = PromptLibrary.from_json_file(path)
        logger.info(f"Prompt library loaded from: {path}")

    def _require_library(self) -> PromptLibrary:
        if self._library is None:
            raise RuntimeError(
                "No prompt library loaded. Call ai.load_library(path) first."
            )
        return self._library

    def send_text_prompt_from_library(self, key: str, values=None) -> str:
        library = self._require_library()
        template, system_prompt = library.get_prompt_with_system_prompt(key)
        if template is None:
            raise KeyError(f"Prompt '{key}' not found in library.")
        user_prompt = template.get_formatted_prompt(values or {})
        effective_system = system_prompt or self._system_prompt
        result = self._text_runner.prompt(
            user_prompt=user_prompt,
            system_prompt=effective_system,
        )
        if result is None:
            raise RuntimeError(
                f"send_text_prompt_from_library failed — the API returned no response. "
                f"Check your model ('{self._config.current_model}') supports the "
                f"attributes set via set_options(): "
                f"{self._text_runner.attributes.to_dict(skip_none=True)}"
            )
        return result.response

    def send_chat_prompt_from_library(self, key: str, values=None) -> str:
        library = self._require_library()
        template, system_prompt = library.get_prompt_with_system_prompt(key)
        if template is None:
            raise KeyError(f"Prompt '{key}' not found in library.")
        user_prompt = template.get_formatted_prompt(values or {})
        effective_system = system_prompt or self._system_prompt
        chat = self._get_chat_runner()
        result = chat.prompt(user_prompt=user_prompt, system_prompt=effective_system)
        if result is None:
            raise RuntimeError(
                f"send_chat_prompt_from_library failed — the API returned no response. "
                f"Check your model ('{self._config.current_model}') supports the "
                f"attributes set via set_options(): "
                f"{self._text_runner.attributes.to_dict(skip_none=True)}"
            )
        return result.response
