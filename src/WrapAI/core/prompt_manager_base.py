# core/prompt_manager_base.py

from pathlib import Path
from typing import Optional, Dict
import logging

from .prompt_library import PromptLibrary
from .prompt_template import PromptTemplate

logger = logging.getLogger(__name__)

class PromptManagerBase:
    def __init__(self, prompt_file_name: str | Path, prompt_names: Dict[str, str]):
        self.prompt_file_name = prompt_file_name
        self.prompt_library: Optional[PromptLibrary] = None
        self.prompt_names = prompt_names  # e.g. { "system": "executive_order_system_prompt", ... }

    def load_prompt_library(self):
        if self.prompt_library is None:
            self.prompt_library = PromptLibrary.from_json_file(self.prompt_file_name)
            logger.info(f"PromptLibrary loaded from {self.prompt_file_name} and added to runtime.")

    def _ensure_loaded(self):
        if self.prompt_library is None:
            self.load_prompt_library()

    def get_prompt(self, logical_key: str) -> Optional[PromptTemplate]:
        """
        Retrieve a prompt by logical name (e.g., 'system', 'summary', 'evaluation').
        """
        self._ensure_loaded()
        prompt_name = self.prompt_names.get(logical_key)
        if not prompt_name:
            logger.warning(f"No prompt mapping for logical key: {logical_key}")
            return None
        prompt_template = self.prompt_library.get_prompt(prompt_name)
        if not prompt_template:
            logger.warning(f"No prompt found with actual name: {prompt_name}")
            return None
        return prompt_template

    def get_prompt_output_schema(self, logical_key: str) -> Optional[dict]:
        """
        Retrieve the output schema from a prompt's attributes if present.
        """
        prompt = self.get_prompt(logical_key)
        if not prompt:
            return None
        response_format = prompt.default_attributes.response_format
        if response_format and "json_schema" in response_format:
            return response_format["json_schema"]
        return None

    def get_prompt_attributes(self, logical_key: str) -> Optional[dict]:
        """
        Return the default attributes of the prompt as a dictionary.
        """
        prompt = self.get_prompt(logical_key)
        if not prompt:
            return None
        return prompt.default_attributes.to_dict()

    def get_system_prompt_text(self, logical_key: str) -> Optional[str]:
        """
        Return the resolved system prompt text for the given prompt.
        """
        prompt = self.get_prompt(logical_key)
        if not prompt:
            return None
        return self.prompt_library.resolve_system_prompt(prompt)
