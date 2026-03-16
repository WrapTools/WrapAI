# providers/venice_provider.py

from typing import Optional

from .provider_base import BaseProvider
from ..prompt.prompt_text import VeniceTextPrompt
from ..core.prompt_response import PromptResponse
from ..info.models import VeniceModels

class VeniceProvider(BaseProvider):
    def __init__(self, api_key: str, model: str):
        super().__init__(api_key, model)
        self.client = VeniceTextPrompt(api_key=api_key, model=model)
        self._models = VeniceModels(api_key)
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

    def get_model_attributes(self, model_name: str, refresh: bool = False) -> dict:
        if refresh:
            self._models.fetch_models()
        return self._models.get_full_model_detail_dict().get(model_name, {})

    def validate_prompt_attributes(self, prompt_attributes: dict, response_type: str) -> tuple[bool, Optional[str]]:
        valid, msg = super().validate_prompt_attributes(prompt_attributes, response_type)
        if not valid:
            return valid, msg

        model_caps = self.get_model_attributes(self.model)
        if not model_caps:
            return True, None

        caps = model_caps.get("capabilities", {})
        if caps.get("custom_attributes") is False and prompt_attributes:
            return False, f"Model '{self.model}' does not support custom attributes."

        return True, None
