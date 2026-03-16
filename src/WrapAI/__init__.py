# WrapAI/__init__.py

import logging

# Create a logger for your library
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# helpers
from .open_provider import open_provider

# In use
from .info.models import ModelRegistry, VeniceModels, OpenAIModels, OPENAI_MODEL_IDS
from .info.account_info import VeniceApiKeyInfo

from .utils.secret_loader import load_secret
from .utils.markdown import MarkdownToTextFromString
from .utils.tokens_char import count_characters_and_tokens
from .utils.file_utils import get_formatted_file_contents

from .core.prompt_manager_base import PromptManagerBase
from .core.prompt_attributes import PromptAttributes, VeniceParameters
from .core.prompt_library import PromptLibrary
from .core.prompt_template import PromptTemplate
from .core.prompt_response import PromptResponse
from .core.wv_core import WEB_SEARCH_MODES, PROVIDER_NAMES, PROVIDER_OPENAI, PROVIDER_VENICE
from .core.default_prompts import CUSTOM_SYSTEM_PROMPT
from .core.provider_config import ProviderConfig
from .core.version import __version__

from .handlers import FILE_HANDLERS

from .prompt.prompt_executor import PromptExecutor
from .prompt.prompt_text import VeniceTextPrompt, OpenAITextPrompt
from .prompt.prompt_chat import VeniceChatPrompt, OpenAIChatPrompt
from .prompt.prompt_chat_memory import ConversationMemory

from .schema.schema_document import DocumentManager
from .schema.schema_json import SchemaBuilder, SchemaField, extract_schema_fields_from_json, reconcile_schema_fields
# from .schema.schema_parser import parse_response_with_schema, format_parsed_as_markdown, format_parsed_as_text, format_parsed_output
from .schema.schema_parser import (
    # SchemaParser,
    # ResponseFormatter,
    # ParseConfig,
    parse_response_with_schema,
    format_parsed_output
)

from .schema.schema_prompt_builder import SchemaPromptBuilder

from .providers.providers import get_provider_instance
from .providers.provider_registry import PROVIDER_CLASSES, VeniceProvider, OpenAIProvider
from .providers.provider_capabilities import ProviderCapabilities, PROVIDER_CAPABILITIES


__all__ = [
    # Library Info
    "__version__",

    # Helpers
    "open_provider",

    # Utility
    "load_secret",
    "MarkdownToTextFromString",
    "count_characters_and_tokens",
    "get_formatted_file_contents",
    "FILE_HANDLERS",

    # Core AI functionality
    "ProviderConfig",
    "PromptExecutor",
    "VeniceTextPrompt",
    "OpenAITextPrompt",
    "VeniceChatPrompt",
    "OpenAIChatPrompt",
    "ConversationMemory",
    "PromptTemplate",
    "PromptResponse",
    "PromptAttributes",
    "VeniceParameters",

    # Management and libraries
    "PromptManagerBase",
    "PromptLibrary",

    # Schema support
    "SchemaBuilder",
    "SchemaField",
    "SchemaPromptBuilder",
    "extract_schema_fields_from_json",
    "reconcile_schema_fields",
    "parse_response_with_schema",
    # "format_parsed_as_markdown",
    # "format_parsed_as_text",
    "format_parsed_output",

    # # New Schema
    # "SchemaParser",
    # "ResponseFormatter",
    # "ParseConfig",

    # Legacy functions (backward compatibility)
    "parse_response_with_schema",
    "format_parsed_output",

    "DocumentManager",

    # Constants and config
    "WEB_SEARCH_MODES",
    "CUSTOM_SYSTEM_PROMPT",

    # Model info and providers
    "ModelRegistry",
    "VeniceModels",
    "OpenAIModels",
    "OPENAI_MODEL_IDS",
    "PROVIDER_CLASSES",
    "PROVIDER_CAPABILITIES",
    "ProviderCapabilities",
    "get_provider_instance",
    "PROVIDER_NAMES",
    "PROVIDER_OPENAI",
    "PROVIDER_VENICE",
    "VeniceProvider",
    "OpenAIProvider",
]

