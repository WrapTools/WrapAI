# providers/providers.py

from .provider_registry import PROVIDER_CLASSES

def get_provider_instance(provider_name: str, api_key: str, model: str):
    provider_cls = PROVIDER_CLASSES.get(provider_name)
    if not provider_cls:
        raise ValueError(f"Unknown provider: {provider_name}")
    return provider_cls(api_key, model)


