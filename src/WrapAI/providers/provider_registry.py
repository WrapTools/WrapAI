# providers/provider_registry.py

from .openai_provider import OpenAIProvider
from .venice_provider import VeniceProvider

from ..core.wv_core import PROVIDER_OPENAI, PROVIDER_VENICE

PROVIDER_CLASSES = {
    PROVIDER_OPENAI: OpenAIProvider,
    PROVIDER_VENICE: VeniceProvider,
}
