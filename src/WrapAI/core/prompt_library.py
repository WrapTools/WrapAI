# core/prompt_library.py

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Optional

from WrapDataclass.core.base import BaseModel
from .prompt_template import PromptTemplate


@dataclass
class PromptLibrary(BaseModel):
    prompts: Dict[str, PromptTemplate] = field(default_factory=dict)

    def list_prompts(self):
        return list(self.prompts.keys())

    def get_prompt(self, name: str) -> Optional[PromptTemplate]:
        return self.prompts.get(name)

    def remove_prompt(self, name: str):
        if name in self.prompts:
            del self.prompts[name]

    def add_prompt(self, name: str, prompt: PromptTemplate):
        self.prompts[name] = prompt

    def get_prompt_with_system_prompt(self, name: str) -> tuple[PromptTemplate, str]:
        prompt = self.get_prompt(name)
        system_prompt = self.resolve_system_prompt(prompt) if prompt else ""
        return prompt, system_prompt

    def resolve_system_prompt(self, prompt: PromptTemplate) -> str:
        if prompt.custom_system_prompt_name:
            custom = self.get_prompt(prompt.custom_system_prompt_name)
            if custom and custom.type == "system":
                return custom.prompt_text
        return prompt.prompt_system_text

    @classmethod
    def from_json_file(cls, file_path: str | Path) -> "PromptLibrary":
        path = Path(file_path)
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        prompts = {
            name: PromptTemplate.from_dict(item)
            for name, item in data.get("data", {}).items()
        }
        return cls(prompts=prompts)
