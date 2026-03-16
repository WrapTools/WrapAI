# prompt/prompt_chat.py
"""
Client for communicating with the Venice AI API.

Includes:
- `VeniceChatPrompt`: Formats prompts, sets attributes, sends API requests,
  and parses structured responses (response + think + memory).
"""

import logging
from typing import Optional, Dict, List

# Logger Configuration
logger = logging.getLogger(__name__)

from .prompt_text import VeniceTextPrompt, OpenAITextPrompt
from .prompt_chat_memory import ConversationMemory
from ..info.models import VeniceModels
from ..core.prompt_response import PromptResponse
from ..core.wv_core import BASE_VENICE_URL, BASE_OPENAI_URL
from ..core.provider_config import ProviderConfig


class VeniceChatPrompt:
    # def __init__(self, api_key: str, model: str, summary_model: Optional[str] = None, base_url: str = BASE_VENICE_URL, **kwargs):
    #     # Initialize the text prompt
    #     self._venice = VeniceTextPrompt(api_key=api_key, model=model, base_url=base_url)
    #     if kwargs:
    #         self._venice.set_attributes(**kwargs)
    #     self._summary_model = summary_model
    #     self.api_key = api_key
    #     self.model = model
    #
    #     # Initialize model token manager
    #     self._models = VeniceModels(api_key)
    #     self._models.fetch_models()
    #
    #     model_token_limit = self._models.get_tokens_by_model_name(model)
    #     if isinstance(model_token_limit, int):
    #         max_context_tokens = model_token_limit
    #     else:
    #         logger.warning(f"Unknown max tokens for model '{model}', defaulting to 8000.")
    #         max_context_tokens = 8000
    #
    #     # Memory setup with dynamic token max
    #     self.memory = ConversationMemory(
    #         system_prompt=kwargs.get('system_prompt', "You are helpful"),
    #         max_tokens=max_context_tokens
    #     )
    #
    #     # Store the parsed response
    #     self.parsed_response: Optional[PromptResponse] = None

    def __init__(self, config_or_key: ProviderConfig | str, model: Optional[str] = None,
                 summary_model: Optional[str] = None, base_url: Optional[str] = None, **kwargs):

        # Handle both ProviderConfig and legacy (api_key + model) formats
        if isinstance(config_or_key, ProviderConfig):
            config = config_or_key
        else:
            config = ProviderConfig(
                name="venice",
                api_key=config_or_key,
                default_model=model or "",
                current_model=model,
                base_url=base_url
            )

        # Store config values
        self.api_key = config.api_key
        self.model = config.get_model()

        # Initialize VeniceTextPrompt
        self._venice = VeniceTextPrompt(config)

        # Set any attributes passed in
        if kwargs:
            self._venice.set_attributes(**kwargs)

        # Store summary model
        self._summary_model = summary_model

        # Initialize model token manager
        self._models = VeniceModels(self.api_key)
        self._models.fetch_models()

        model_token_limit = self._models.get_tokens_by_model_name(self.model)
        if isinstance(model_token_limit, int):
            max_context_tokens = model_token_limit
        else:
            logger.warning(f"Unknown max tokens for model '{self.model}', defaulting to 8000.")
            max_context_tokens = 8000

        # Memory setup with dynamic token max
        self.memory = ConversationMemory(
            system_prompt=kwargs.get('system_prompt', "You are helpful"),
            max_tokens=max_context_tokens
        )

        self.parsed_response: Optional[PromptResponse] = None

    # Attribute change methods
    def __getattr__(self, name):
        """Automatically delegate undefined attributes/methods to _venice"""
        return getattr(self._venice, name)

    def set_model(self, model_id: str) -> None:
        """Sets a new model and updates token limit if available."""
        self._venice.model = model_id
        self.model = model_id
        self._ensure_models_loaded()

        model_token_limit = self._models.get_tokens_by_model_name(model_id)
        if isinstance(model_token_limit, int):
            self.memory.max_tokens = model_token_limit
        else:
            logger.warning(f"Unknown max tokens for model '{model_id}', keeping previous value.")

    # def set_attributes(self, **kwargs) -> None:
    #     """Pass attributes to the underlying text prompt."""
    #     self._venice.set_attributes(**kwargs)

    def set_attributes(self, **kwargs) -> None:
        """Pass attributes to the underlying text prompt, handling venice_parameters specially."""
        # Handle venice_parameters separately
        venice_params = kwargs.pop('venice_parameters', None)

        # Pass the remaining attributes to the text prompt
        if kwargs:
            self._venice.set_attributes(**kwargs)

        # Handle venice_parameters with proper parameter name conversion
        if isinstance(venice_params, dict):
            # Convert any legacy parameter names to new ones
            updated_params = {}

            # Parameter name mapping from old to new
            param_mapping = {
                'web_search': 'enable_web_search',
                # Add other mappings as needed
            }

            for param_name, param_value in venice_params.items():
                # Check if this is a legacy parameter name that needs conversion
                if param_name in param_mapping:
                    new_name = param_mapping[param_name]
                    logger.info(f"Converting legacy parameter '{param_name}' to '{new_name}'")
                    updated_params[new_name] = param_value
                else:
                    updated_params[param_name] = param_value

            # Now set the updated parameters
            try:
                self._venice.set_attributes(venice_parameters=updated_params)
            except Exception as e:
                logger.error(f"Failed to set venice_parameters: {e}")
                logger.info("Parameters attempted: " + str(updated_params))

    def _ensure_models_loaded(self) -> None:
        """Make sure model data is loaded."""
        if not self._models.models_data:
            self._models.fetch_models()

    # Prompt methods
    def prompt(self, user_prompt: str, system_prompt: Optional[str] = None) -> Optional[PromptResponse]:
        """Send a prompt with memory management."""
        # Memory handling logic
        if system_prompt:
            self.memory.update_system_prompt(system_prompt)

        self.memory.add_message("user", user_prompt)

        # Send the request with the full message history
        response_dict = self._venice.prompt(user_prompt=user_prompt, messages=self.memory.message_history)

        # Convert the response dict to a PromptResponse object if needed
        if response_dict:
            if isinstance(response_dict, PromptResponse):
                self.parsed_response = response_dict
            elif isinstance(response_dict, dict):
                # For backward compatibility, convert dict to PromptResponse
                self.parsed_response = PromptResponse(
                    model=response_dict.get('model'),
                    created=response_dict.get('created'),
                    usage=response_dict.get('usage', {}),
                    think=response_dict.get('think', ''),
                    response=response_dict.get('response', ''),
                    citations=response_dict.get('citations', []),
                    parameters=response_dict.get('parameters', {}),
                    system_prompt=self.memory.messages[0]['content'] if self.memory.messages else '',
                    user_prompt=user_prompt,
                    # conversation_history=self.memory.message_history
                )
            else:
                logger.warning(f"Unexpected response type: {type(response_dict)}")
                self.parsed_response = None

            # Add the assistant's response to memory
            self.memory.add_message("assistant", self.parsed_response.response)

        return self.parsed_response

    def summarize_memory(self, summary_prompt: str = "Summarize this conversation.",
                         model_override: Optional[str] = None, buffer: int = 2000) -> Optional[str]:
        """
        Summarizes the current memory using the chat model (or optional override).
        Trims memory to fit within token limits of the selected model.
        """
        summary_model = model_override or self._summary_model or self.model
        messages = self.get_trimmed_messages_for_model(summary_model, summary_prompt, buffer)

        temp_venice = VeniceTextPrompt(api_key=self.api_key, model=summary_model)

        try:
            response = temp_venice.prompt(user_prompt=summary_prompt, messages=messages)
            if response:
                if isinstance(response, PromptResponse):
                    # Add explicit type check for response.response
                    if hasattr(response, 'response') and isinstance(response.response, str):
                        return response.response.strip()
                    return str(response.response) if hasattr(response, 'response') else ""
                elif isinstance(response, dict):
                    response_text = response.get("response", "")
                    return response_text.strip() if isinstance(response_text, str) else str(response_text)
            return "Summary not available."
        except Exception as e:
            logger.error(f"Error during summarization: {e}")
            return "Summary failed due to an error."

    def get_trimmed_messages_for_model(self, model: str, summary_prompt: str, buffer: int = 1000) -> List[
        Dict[str, str]]:
        """
        Returns a version of memory + summary_prompt that fits within the given model's token limit.
        """
        self._ensure_models_loaded()
        model_token_limit = self._models.get_tokens_by_model_name(model)
        if not isinstance(model_token_limit, int):
            logger.warning(f"Unknown token limit for model '{model}'. Using current memory limit.")
            model_token_limit = self.memory.max_tokens

        # Estimate token cost of summary prompt
        summary_prompt_tokens = self.memory.calculate_tokens(summary_prompt)
        target_limit = model_token_limit - buffer - summary_prompt_tokens

        # Start with system message
        trimmed = [self.memory.messages[0]] if self.memory.messages and self.memory.messages[0][
            "role"] == "system" else []
        current_tokens = self.memory.calculate_tokens(trimmed[0]["content"]) if trimmed else 0

        # Track if we had to exclude any messages
        total_messages = len(self.memory.messages)
        messages_included = len(trimmed)

        # Add most recent messages in reverse order until we hit the target
        for msg in reversed(self.memory.messages[1:] if trimmed else self.memory.messages):
            msg_tokens = self.memory.calculate_tokens(msg["content"])
            if current_tokens + msg_tokens > target_limit:
                # We can't add this message without exceeding the limit
                break
            trimmed.insert(1, msg)
            current_tokens += msg_tokens
            messages_included += 1

        # Add the summary prompt
        trimmed.append({"role": "user", "content": summary_prompt})

        # Log whether trimming occurred
        if messages_included < total_messages:
            logger.warning(f"⚠️ Trimmed conversation: included {messages_included}/{total_messages} messages "
                           f"({current_tokens} tokens) to fit {model} with buffer {buffer}")
        else:
            logger.info(f"✅ Included all {messages_included} messages ({current_tokens} tokens) for {model} "
                        f"with buffer {buffer}")

        return trimmed

    def trim_and_summarize_if_needed(self, summary_prompt: str = "Summarize this conversation.", model_override: Optional[str] = None) -> None:
        """
        Summarizes and resets memory if nearing token limit.
        """
        if self.memory.token_count > self.memory.max_tokens * 0.8:
            summary = self.summarize_memory(summary_prompt, model_override)
            self.memory.reset_with_summary(summary)

    # Clear memory method
    def clear_memory(self) -> None:
        """Reset the conversation memory."""
        self.memory.reset()

    # Accessor methods for compatibility
    def get_response(self) -> str:
        """Get the response text from the last API call."""
        return self.parsed_response.response if self.parsed_response else ""

    def get_think(self) -> str:
        """Get the thinking section from the last API call."""
        return self.parsed_response.think if self.parsed_response else ""

    def get_usage(self) -> Dict:
        """Get token usage information from the last API call."""
        return self.parsed_response.usage if self.parsed_response else {}

    def get_model(self) -> str:
        """Get the model name used for the last API call."""
        return self.parsed_response.model if self.parsed_response else self.model


class OpenAIChatPrompt:
    # def __init__(self, api_key: str, model: str, system_prompt: str = "You are helpful", **kwargs):
    #     self._openai = OpenAITextPrompt(api_key=api_key, model=model)
    #     if kwargs:
    #         self._openai.set_attributes(**kwargs)
    #
    #     self.api_key = api_key
    #     self.model = model
    #     self.memory = ConversationMemory(system_prompt=system_prompt, max_tokens=8000)
    #     self.parsed_response: Optional[PromptResponse] = None

    def __init__(self, config_or_key: ProviderConfig | str, model: Optional[str] = None,
                 system_prompt: str = "You are helpful", **kwargs):

        # Handle both ProviderConfig and legacy formats
        if isinstance(config_or_key, ProviderConfig):
            config = config_or_key
        else:
            config = ProviderConfig(
                name="openai",
                api_key=config_or_key,
                default_model=model or "",
                current_model=model
            )

        # Store for reference
        self.api_key = config.api_key
        self.model = config.get_model()

        # Initialize OpenAITextPrompt
        self._openai = OpenAITextPrompt(config)

        if kwargs:
            self._openai.set_attributes(**kwargs)

        # Memory and response
        self.memory = ConversationMemory(system_prompt=system_prompt, max_tokens=8000)
        self.parsed_response: Optional[PromptResponse] = None

    def __getattr__(self, name):
        return getattr(self._openai, name)

    def prompt(self, user_prompt: str, system_prompt: Optional[str] = None) -> Optional[PromptResponse]:
        if system_prompt:
            self.memory.update_system_prompt(system_prompt)

        self.memory.add_message("user", user_prompt)

        response = self._openai.prompt(
            user_prompt=user_prompt,
            messages=self.memory.message_history
        )

        if response:
            if isinstance(response, PromptResponse):
                self.parsed_response = response
            elif isinstance(response, dict):
                self.parsed_response = PromptResponse(
                    model=response.get('model'),
                    created=response.get('created'),
                    usage=response.get('usage', {}),
                    response=response.get('response', ''),
                    think=response.get('think', ''),
                    citations=response.get('citations', []),
                    parameters=response.get('parameters', {}),
                    system_prompt=self.memory.messages[0]["content"],
                    user_prompt=user_prompt,
                )
            self.memory.add_message("assistant", self.parsed_response.response)

        return self.parsed_response

    def summarize_memory(self, summary_prompt: str = "Summarize this conversation.") -> Optional[str]:
        messages = self.memory.message_history + [{"role": "user", "content": summary_prompt}]
        response = self._openai.prompt(user_prompt=summary_prompt, messages=messages)

        if isinstance(response, PromptResponse):
            return response.response
        elif isinstance(response, dict):
            return response.get("response", "")
        return "Summary not available."

    def trim_and_summarize_if_needed(self, threshold: float = 0.8):
        if self.memory.token_count > self.memory.max_tokens * threshold:
            summary = self.summarize_memory()
            self.memory.reset_with_summary(summary)

    def clear_memory(self):
        self.memory.reset()

    def get_response(self):
        return self.parsed_response.response if self.parsed_response else ""

    def get_think(self):
        return self.parsed_response.think if self.parsed_response else ""

    def get_usage(self) -> Dict:
        return self.parsed_response.usage if self.parsed_response else {}

    def get_model(self) -> str:
        return self.parsed_response.model if self.parsed_response else self.model