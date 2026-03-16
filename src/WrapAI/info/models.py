# info/models.py

import requests
import logging

from ..core.wv_core import BASE_VENICE_URL, BASE_OPENAI_URL, OPENAI_MODEL_IDS, PROVIDER_OPENAI, PROVIDER_VENICE

# Logger Configuration
logger = logging.getLogger(__name__)

class VeniceModels:
    def __init__(self, api_key, base_url=BASE_VENICE_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.models_data = []  # To store models data after fetching

    def __repr__(self):
        return f"<{self.__class__.__name__}: {len(self.models_data)} models loaded>"

    # Fetch method
    def fetch_models(self):
        """Fetches the models from the API and stores them in the instance."""
        url = f"{self.base_url}/models"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_json = response.json()
            self.models_data = response_json.get("data", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
            self.models_data = []

    # Get methods
    def get_model_names(self):
        """Returns a list of model names (IDs)."""
        return [model.get("id", "N/A") for model in self.models_data]

    def get_owners_dict(self):
        return {model["id"]: model.get("owned_by", "unknown") for model in self.models_data}

    def get_model_tokens_dict(self):
        """Returns a dictionary mapping model names to their available context tokens."""
        return {
            model.get("id", "N/A"): model.get("model_spec", {}).get("availableContextTokens", "N/A")
            for model in self.models_data
        }

    def get_tokens_by_model_name(self, model_name):
        """Returns the available context tokens for a specific model name."""
        for model in self.models_data:
            if model.get("id") == model_name:
                return model.get("model_spec", {}).get("availableContextTokens", "N/A")
        return "Model not found"

    def get_full_model_detail_dict(self):
        """
            Returns a dictionary mapping model names to the entire model dict (all specs and capabilities).
        """
        detail_dict = {}
        for model in self.models_data:
            model_id = model.get("id", "N/A")
            detail_dict[model_id] = model
        return detail_dict

    def filter_by_capability(self, capability_key: str):
        return [m for m in self.models_data if m.get("model_spec", {}).get("capabilities", {}).get(capability_key)]

    def get_chat_models(self):
        return [m for m in self.models_data if m.get("type") == "chat"]

    def get_reasoning_models(self):
        return self.filter_by_capability("supportsReasoning")

    def get_output_schema_models(self):
        return self.filter_by_capability("supportsResponseSchema")


class OpenAIModels:
    def __init__(self, api_key, base_url=BASE_OPENAI_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.models_data = []
        self._build_static_models()

    def __repr__(self):
        return f"<{self.__class__.__name__}: {len(self.models_data)} models (static)>"

    def _build_static_models(self):
        """Manually defines static model metadata for OpenAI."""
        self.models_data = [
            {
                "id": model_id,
                "owned_by": "openai",
                "model_spec": {
                    "capabilities": {
                        "supportsReasoning": True,
                        "supportsResponseSchema": True
                    },
                    "availableContextTokens": 8192
                }
            }
            for model_id in OPENAI_MODEL_IDS
        ]

    def fetch_models(self):
        """No-op for OpenAI – already loaded statically."""
        logger.info("Skipping OpenAI fetch_models(); using static model list.")

    def get_model_names(self):
        return [model["id"] for model in self.models_data]

    def get_owners_dict(self):
        return {model["id"]: model.get("owned_by", "unknown") for model in self.models_data}

    def get_full_model_detail_dict(self):
        return {model["id"]: model for model in self.models_data}

    def filter_by_capability(self, capability_key: str):
        return [m for m in self.models_data if m.get("model_spec", {}).get("capabilities", {}).get(capability_key)]

    def get_chat_models(self):
        return [m for m in self.models_data if m.get("id", "").startswith("gpt")]

class ModelRegistry:
    def __init__(self, provider: str, api_key: str):
        # provider = provider.lower()
        if provider == PROVIDER_VENICE:
            self.registry = VeniceModels(api_key)
        elif provider == PROVIDER_OPENAI:
            self.registry = OpenAIModels(api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def fetch_models(self):
        self.registry.fetch_models()

    def list_models(self):
        return self.registry.get_model_names()

    def get_model_details(self, model_id):
        return self.registry.get_full_model_detail_dict().get(model_id, {})

    def get_all(self):
        return self.registry.get_full_model_detail_dict()

