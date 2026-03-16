# providers/openai_provider.py

from typing import Optional

from .provider_capabilities import PROVIDER_CAPABILITIES
from .provider_base import BaseProvider
from ..prompt.prompt_text import OpenAITextPrompt
from ..core.prompt_response import PromptResponse
from ..info.models import OpenAIModels


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str, model: str):
        super().__init__(api_key, model)
        self.client = OpenAITextPrompt(api_key=api_key, model=model)
        self._models = OpenAIModels(api_key)
        self._models.fetch_models()

    def run(self, prompt_text: str):
        """
        Run method expected by PromptExecutor. Sends prompt as user_prompt only.
        """
        return self.client.prompt(user_prompt=prompt_text)

    def send_prompt(self, prompt: dict) -> Optional[PromptResponse]:
        return self.client.prompt(**prompt)

    def set_attributes(self, **kwargs):
        self.client.set_attributes(**kwargs)

    def get_response(self):
        return self.client.get_response()

    def get_model_attributes(self, model_name: str, refresh: bool = False) -> dict:
        if refresh or not self._models.models_data:
            self._models.fetch_models()
        return self._models.get_full_model_detail_dict().get(model_name, {})

    def validate_prompt_attributes(self, prompt_attributes: dict, response_type: str) -> tuple[bool, Optional[str]]:
        valid, msg = super().validate_prompt_attributes(prompt_attributes, response_type)
        if not valid:
            return valid, msg

        caps = PROVIDER_CAPABILITIES["OpenAI"].get_model_capabilities(self.model)
        if not caps:
            return True, None

        # Fix: Access capabilities attribute instead of treating caps as dict
        capabilities = caps.capabilities if hasattr(caps, 'capabilities') else {}

        if capabilities.get("custom_attributes") is False and prompt_attributes:
            # Allow response_format and empty/default venice_parameters
            filtered_attributes = {}

            for k, v in prompt_attributes.items():
                if k == "response_format":
                    continue  # Always allow response_format
                elif k == "venice_parameters":
                    # Check if venice_parameters has any actual values
                    if hasattr(v, 'to_dict'):
                        venice_dict = v.to_dict(skip_none=True)
                        if venice_dict:  # Only block if it has actual values
                            filtered_attributes[k] = v
                    elif isinstance(v, dict) and v:  # Non-empty dict
                        filtered_attributes[k] = v
                    # Skip empty venice_parameters
                else:
                    filtered_attributes[k] = v

            if filtered_attributes:
                blocked_attrs = list(filtered_attributes.keys())
                return False, f"Model '{self.model}' does not support custom attributes. Blocked: {blocked_attrs}. Only 'response_format' is allowed."

        return True, None


