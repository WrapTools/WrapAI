# core/wv_core.py

# from enum import Enum
from dataclasses import dataclass

BASE_VENICE_URL="https://api.venice.ai/api/v1"
BASE_OPENAI_URL="https://api.openai.com/v1"

KEY_URL = "https://api.venice.ai/api/v1/api_keys"
RATE_LIMIT_API_URL = "https://api.venice.ai/api/v1/api_keys/rate_limits"
RATE_LIMIT_MODEL_URL = "https://api.venice.ai/api/v1/api_keys/rate_limits/log"

WEB_SEARCH_MODES = ["auto", "on", "off",]

PROMPT_TYPE_QUESTION = "question"
PROMPT_TYPE_CHAT = "chat"
PROMPT_TYPES = [PROMPT_TYPE_QUESTION, PROMPT_TYPE_CHAT]


@dataclass(frozen=True)
class WSChatMemoryDefaults:
    MAX_TOKENS: int = 8000
    TOKEN_BUFFER: int = 512

# =============================

# Providers
PROVIDER_OPENAI = "OpenAI"
PROVIDER_VENICE = "Venice"
PROVIDER_NAMES = [PROVIDER_OPENAI, PROVIDER_VENICE]

MODEL_O4_MINI = "o4-mini"
MODEL_GPT_4_1_MINI = "gpt-4.1-mini"
MODEL_GPT_4_1_NANO = "gpt-4.1-nano"

OPENAI_MODEL_IDS = [MODEL_O4_MINI, MODEL_GPT_4_1_MINI, MODEL_GPT_4_1_NANO]

# Roles
ROLE_SYSTEM = "system"
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
STANDARD_ROLES = [ROLE_SYSTEM, ROLE_USER, ROLE_ASSISTANT]

@dataclass(frozen=True)
class ModelInfo:
    reasoning: bool
    response_schema: bool
    custom_attributes: bool
    context_length: int
