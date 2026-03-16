# core/prompt_runtime_manager.py

from pathlib import Path
from typing import Optional
from collections.abc import Iterator


from .prompt_manager_base import PromptManagerBase
from .prompt_template import PromptTemplate
from .prompt_response import PromptResponse
from ..providers.providers import get_provider_instance
from ..providers.provider_capabilities import  PROVIDER_CAPABILITIES

from ..utils.tokens_char import count_characters_and_tokens, split_text_to_token_chunks

from .provider_config import ProviderConfig

class PromptRuntimeManager:
    def __init__(self, provider_configs: dict, prompt_file: Path, prompt_names: dict):
        self._provider_configs = provider_configs
        self._active_provider_name: Optional[str] = None
        self._provider_instance = None

        self.prompt_manager = PromptManagerBase(prompt_file_name=prompt_file, prompt_names=prompt_names)
        self.prompt_manager.load_prompt_library()

    def set_provider(self, provider_name: str):
        config = self._provider_configs.get(provider_name)
        if not config:
            raise ValueError(f"Provider config not found: {provider_name}")

        self._provider_instance = get_provider_instance(
            provider_name,
            config.api_key,
            config.get_model()
        )
        self._active_provider_name = provider_name

    def run_prompt(self, logical_key: str, values: dict) -> Optional[PromptResponse]:
        if self._provider_instance is None:
            raise RuntimeError("No provider has been set")

        template: PromptTemplate = self.prompt_manager.get_prompt(logical_key)
        if not template:
            raise ValueError(f"No prompt template found for key: {logical_key}")

        formatted_prompt = template.get_formatted_prompt(values)
        system_prompt = self.prompt_manager.get_system_prompt_text(logical_key)

        attributes = template.default_attributes.to_dict()

        # ✅ Step 1: Set attributes
        self._provider_instance.set_attributes(**attributes)

        # ✅ Step 2: Only pass prompt fields to send_prompt()
        return self._provider_instance.send_prompt({
            "user_prompt": formatted_prompt,
            "system_prompt": system_prompt,
        })

    def get_current_provider(self):
        return self._active_provider_name

    def list_available_models(self, provider_name: str) -> list:
        caps = PROVIDER_CAPABILITIES.get(provider_name)
        return caps.list_models() if caps else []

    def get_prompt_template(self, key: str) -> Optional[PromptTemplate]:
        return self.prompt_manager.get_prompt(key)

    def get_provider_config(self, name: str) -> ProviderConfig:
        return self._provider_configs[name]

    def set_api_key(self, provider: str, api_key: str):
        self._provider_configs[provider].api_key = api_key

    def set_current_model(self, provider: str, model: str):
        self._provider_configs[provider].current_model = model

    # --------------- NEW ----------------------------
    def get_provider_instance(self):
        if self._provider_instance is None:
            raise RuntimeError("No provider has been set")
        return self._provider_instance

    def stream_prompt(self, logical_key: str, values: dict) -> Iterator[str]:
        """
        Stream token deltas for the same logical_key you pass to run_prompt().
        Mirrors run_prompt() but calls the underlying runner's prompt_stream().
        """
        provider = self.get_provider_instance()

        template: PromptTemplate = self.prompt_manager.get_prompt(logical_key)
        if not template:
            raise ValueError(f"No prompt template found for key: {logical_key}")

        formatted_prompt = template.get_formatted_prompt(values)
        system_prompt = self.prompt_manager.get_system_prompt_text(logical_key)
        attributes = template.default_attributes.to_dict()

        # keep same behavior as run_prompt()
        provider.set_attributes(**attributes)

        runner = provider.get_text_prompt_runner()
        yield from runner.prompt_stream(
            user_prompt=formatted_prompt,
            system_prompt=system_prompt,
        )

    def stream_prompt_collect(self, logical_key: str, values: dict) -> str:
        """
        Convenience: stream_prompt -> accumulate -> return full text.
        """
        return "".join(self.stream_prompt(logical_key, values))
