# schema_prompt_builder.py

from typing import List
from .schema_json import SchemaField

class SchemaPromptBuilder:
    def __init__(self, schema_fields: List[SchemaField]):
        self.schema_fields = schema_fields

    def generate_prompt_section(self, include_descriptions: bool = True) -> str:
        prompt_lines = ["Please produce a JSON object with the following fields:"]
        for field in self.schema_fields:
            line = f"- `{field.name}` ({self.human_readable_type(field)})"
            if include_descriptions and field.description:
                line += f": {field.description}"
            prompt_lines.append(line)
        return "\n".join(prompt_lines)

    def human_readable_type(self, field: SchemaField) -> str:
        if field.type == "array" and field.item_type:
            return f"array of {field.item_type}s"
        elif field.type == "enum" and field.enum_values:
            return f"enum: {', '.join(repr(v) for v in field.enum_values)}"
        elif field.type == "const" and field.value is not None:
            return f"constant: {repr(field.value)}"
        else:
            return field.type

    def generate_full_prompt(self, additional_context: str = "") -> str:
        section = self.generate_prompt_section()
        if additional_context:
            return f"{additional_context}\n\n{section}"
        return section
