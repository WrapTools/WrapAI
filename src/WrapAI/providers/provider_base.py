# providers/provider_base.py

from typing import Optional

class BaseProvider:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def send_prompt(self, prompt: dict) -> str:
        raise NotImplementedError("Each provider must implement send_prompt()")

    def get_model_attributes(self, model_name: str, refresh: bool = False) -> dict:
        raise NotImplementedError("Each provider must implement get_model_attributes()")

    def validate_prompt_attributes(self, prompt_attributes: dict, response_type: str) -> tuple[bool, Optional[str]]:
        # Default: no validation failure
        return True, None

    def get_text_prompt_runner(self):
        """
        Expose the underlying TextPrompt client (e.g. VeniceTextPrompt or OpenAITextPrompt)
        so you can call .set_attributes(...) and .prompt(...) on it directly.
        """
        if hasattr(self, "client"):
            return self.client
        raise AttributeError("This provider has no .client to unwrap — did you subclass BaseProvider correctly?")
