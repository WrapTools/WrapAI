# core/prompt_attributes.py

from dataclasses import dataclass, field
from typing import Optional, Any, Dict, List

import logging

# Logger Configuration
logger = logging.getLogger(__name__)

from WrapDataclass.core.base import BaseModel

from .wv_core import WEB_SEARCH_MODES

@dataclass
class OpenAIPromptAttributes(BaseModel):
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    max_completion_tokens: Optional[int] = None
    stop: Optional[List[str]] = None
    # stream: Optional[bool] = None # PROMPT NEEDS TO CHANGE BEFORE THIS CAN BE USED
    n: Optional[int] = None
    user: Optional[str] = None
    parallel_tool_calls: Optional[bool] = None
    tools: Optional[Any] = None
    tool_choice: Optional[Dict[str, Any]] = None
    # stream_options: Optional[Dict[str, Any]] = None
    response_format: Optional[Dict[str, Any]] = None
    # Need to implement
    # logit_bias: Optional[Dict[int, float]] = None
    # logprobs: Optional[int] = None
    # echo: Optional[bool] = None
    # best_of: Optional[int] = None
    # suffix: Optional[str] = None
    # top_k: Optional[int] = None
    # inject_start_text: Optional[str] = None
    # inject_restart_text: Optional[str] = None

    def __post_init__(self):
        if self.temperature is not None and not (0 <= self.temperature <= 2):
            raise ValueError("temperature must be between 0 and 2.")
        if self.top_p is not None and not (0 <= self.top_p <= 1):
            raise ValueError("top_p must be between 0 and 1.")
        if self.frequency_penalty is not None and not (-2 <= self.frequency_penalty <= 2):
            raise ValueError("frequency_penalty must be between -2 and 2.")
        if self.presence_penalty is not None and not (-2 <= self.presence_penalty <= 2):
            raise ValueError("presence_penalty must be between -2 and 2.")
        # Need to implementation and use actual values
        # if self.logit_bias is not None:
        #     for bias in self.logit_bias.values():
        #         if not -100 <= bias <= 100:
        #             raise ValueError("logit_bias values must be between -100 and 100.")
        # if self.top_k is not None and not (0 <= self.top_k):  # OpenAI has no upper bound for top_k
        #     raise ValueError("top_k must be a non-negative integer.")
        # if self.best_of is not None and not (1 <= self.best_of <= 20):
        #     raise ValueError("best_of must be between 1 and 20.")
        # if self.logprobs is not None and not (0 <= self.logprobs <= 5):
        #     raise ValueError("logprobs must be between 0 and 5.")


@dataclass
class VeniceParameters(BaseModel):
    enable_web_search: Optional[str] = None
    include_venice_system_prompt: Optional[bool] = None
    character_slug: Optional[str] = None
    strip_thinking_response: Optional[bool] = None
    disable_thinking: Optional[bool] = None
    enable_web_citations: Optional[bool] = None



    def __post_init__(self):
        if self.enable_web_search is not None and self.enable_web_search not in WEB_SEARCH_MODES:
            raise ValueError(f"enable_web_search must be one of {WEB_SEARCH_MODES}, got '{self.enable_web_search}'")

@dataclass
class VenicePromptAttributes(OpenAIPromptAttributes):
    venice_parameters: VeniceParameters = field(default_factory=VeniceParameters)

    def __post_init__(self):
        super().__post_init__()

        # Convert dict to VeniceParameters if passed as dict
        if isinstance(self.venice_parameters, dict):
            logger.warning(
                "VenicePromptAttributes: 'venice_parameters' was provided as a dict. Converting to VeniceParameters dataclass."
            )
            self.venice_parameters = VeniceParameters.from_dict(self.venice_parameters)

# For backward compatibility
PromptAttributes = VenicePromptAttributes
