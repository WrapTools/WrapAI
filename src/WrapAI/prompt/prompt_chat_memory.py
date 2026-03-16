# prompt/prompt_chat_memory.py
"""
Conversation memory manager for AI chat sessions.

Includes:
- `ConversationMemory`: Tracks messages, manages token limits, trims history,
  and supports system prompt updates and summarization.
"""

import logging
from typing import List, Dict, Any, Optional

# Logger Configuration
logger = logging.getLogger(__name__)

from ..utils.tokens_char import count_characters_and_tokens
from ..core.wv_core import WSChatMemoryDefaults


class ConversationMemory:
    def __init__(self, system_prompt: str = "",
                 max_tokens: int = WSChatMemoryDefaults.MAX_TOKENS,
                 token_buffer: int = WSChatMemoryDefaults.TOKEN_BUFFER):
        self.messages: List[Dict[str, str]] = []
        self.max_tokens: int = max_tokens
        self.token_buffer: int = token_buffer
        self.current_tokens: int = 0

        if system_prompt:
            self.add_message("system", system_prompt)

    def update_system_prompt(self, prompt: str) -> None:
        """Update or add the system prompt at the beginning of the conversation."""
        if self.messages and self.messages[0]["role"] == "system":
            old_tokens = self.calculate_tokens(self.messages[0]["content"])
            self.messages[0]["content"] = prompt
            new_tokens = self.calculate_tokens(prompt)
            self.current_tokens = self.current_tokens - old_tokens + new_tokens
        else:
            self.messages.insert(0, {"role": "system", "content": prompt})
            self.current_tokens += self.calculate_tokens(prompt)

    def reset(self) -> None:
        """Clear all messages from memory."""
        self.messages = []
        self.current_tokens = 0

    def add_message(self, role: str, content: str) -> None:
        """Add message to memory with automatic trimming if needed."""
        if role not in {"user", "assistant", "system"}:
            logger.warning(f"Unexpected role '{role}' in message.")

        new_msg = {"role": role, "content": content}
        tokens = self.calculate_tokens(content)

        if self._will_exceed_limit(tokens):
            self.trim_messages(tokens)

        self.messages.append(new_msg)
        self.current_tokens += tokens

    def trim_messages(self, incoming_tokens: int = 0) -> None:
        """Remove oldest non-system messages until under token limit."""
        target = self.max_tokens - self.token_buffer - incoming_tokens
        while self.current_tokens > target and len(self.messages) > 1:
            # Keep system prompt (index 0), remove oldest message after that (index 1)
            removed = self.messages.pop(1)
            removed_tokens = self.calculate_tokens(removed["content"])
            self.current_tokens -= removed_tokens
            logger.debug(f"Trimmed message with {removed_tokens} tokens to stay under limit")

    def reset_with_summary(self, summary: str) -> None:
        """Replace memory with summary and preserve recent context."""
        system_msg = self.messages[0] if self.messages and self.messages[0]["role"] == "system" else {"role": "system", "content": ""}

        # Preserve last 2 exchanges (up to 4 messages: 2 user, 2 assistant)
        recent = self.messages[-4:] if len(self.messages) >= 4 else self.messages[1:] if len(self.messages) > 1 else []

        # New message list with system prompt + summary and recent messages
        self.messages = [
            {
                "role": system_msg["role"],
                "content": f"{system_msg['content']}\nSUMMARY: {summary}"
            }
        ] + recent

        # Recalculate tokens
        self.current_tokens = sum(
            self.calculate_tokens(msg["content"])
            for msg in self.messages
        )

    def calculate_tokens(self, text: str) -> int:
        """Calculate the number of tokens in a text string."""
        _, tokens = count_characters_and_tokens(text)
        return tokens

    def _will_exceed_limit(self, incoming: int) -> bool:
        """Check if adding incoming tokens would exceed the limit."""
        return (self.current_tokens + incoming) > (self.max_tokens - self.token_buffer)

    @property
    def message_history(self) -> List[Dict[str, str]]:
        """Return a copy of the current message history."""
        return self.messages.copy()

    @property
    def token_count(self) -> int:
        """Return the current token count."""
        return self.current_tokens
