# core/provider_config.py

from dataclasses import dataclass
from typing import Optional

from ..core.wv_core import BASE_OPENAI_URL, BASE_VENICE_URL, PROVIDER_OPENAI, PROVIDER_VENICE

@dataclass
class ProviderConfig:
    name: str
    api_key: str
    default_model: str
    current_model: Optional[str] = None
    base_url: Optional[str] = None

    def __post_init__(self):
        if not self.base_url:
            self.base_url = self._get_default_base_url(self.name)

    def get_model(self):
        return self.current_model or self.default_model

    @staticmethod
    def _get_default_base_url(name: str) -> str:
        if name == PROVIDER_OPENAI:
            return BASE_OPENAI_URL
        elif name == PROVIDER_VENICE:
            return BASE_VENICE_URL
        raise ValueError(f"Unknown provider name: {name}")
