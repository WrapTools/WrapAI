# core/prompt_response.py

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from WrapDataclass.core.base import BaseModel

from .prompt_attributes import PromptAttributes

@dataclass
class PromptResponse(BaseModel):
    model: Optional[str] = None
    created: Optional[str] = None
    usage: Optional[Dict[str, Any]] = field(default_factory=dict)
    think: Optional[str] = None
    response: Optional[str] = None
    citations: Optional[List[str]] = field(default_factory=list)
    parameters: Optional[Dict[str, Any]] = field(default_factory=dict)
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    _cached_attrs: Optional[PromptAttributes] = field(default=None, init=False, repr=False)

    @property
    def as_prompt_attributes(self) -> PromptAttributes:
        if self._cached_attrs is None:
            self._cached_attrs = PromptAttributes.from_dict(self.parameters or {})
        return self._cached_attrs

    def get_prompt_attributes(self) -> PromptAttributes:
        return PromptAttributes.from_dict(self.parameters or {})