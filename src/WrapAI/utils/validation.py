# utils/validation.py

# IN DEVELOPMENT

from ..providers.providers import get_provider_instance

def validate_prompt(provider_name, api_key, model, prompt_attributes, response_type):
    provider = get_provider_instance(provider_name, api_key, model)
    return provider.validate_prompt_attributes(prompt_attributes, response_type)
