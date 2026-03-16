# providers/provider_capabilities.py

from typing import Dict

from ..core.wv_core import PROVIDER_OPENAI, PROVIDER_VENICE, MODEL_O4_MINI, MODEL_GPT_4_1_MINI, MODEL_GPT_4_1_NANO, ModelInfo

class ProviderCapabilities:
    def __init__(self, models: Dict[str, ModelInfo]):
        self.models = models

    def get_display_info(self, model_name: str) -> str:
        model = self.models.get(model_name)
        if model:
            return (
                f"reasoning: {model.reasoning}, "
                f"response_schema: {model.response_schema}, "
                f"custom_attributes: {model.custom_attributes}, "
                f"context_length: {model.context_length}"
            )
        return "Model not found"

    def list_models(self):
        return list(self.models.keys())

    def get_model_capabilities(self, model_name: str) -> ModelInfo | None:
        return self.models.get(model_name)


PROVIDER_CAPABILITIES = {
    PROVIDER_OPENAI: ProviderCapabilities({
        MODEL_O4_MINI: ModelInfo(
            reasoning=True,
            response_schema=True,
            custom_attributes=False,
            context_length=128000,
        ),
        MODEL_GPT_4_1_MINI: ModelInfo(
            reasoning=False,
            response_schema=True,
            custom_attributes=True,
            context_length=1000000,
        ),
        MODEL_GPT_4_1_NANO: ModelInfo(
            reasoning=False,
            response_schema=True,
            custom_attributes=True,
            context_length=1000000,
        ),
    }),
    PROVIDER_VENICE: None,  # dynamic
}


