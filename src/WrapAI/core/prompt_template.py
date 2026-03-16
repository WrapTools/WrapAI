# core/prompt_template.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional
import re
import hashlib
import logging

from WrapDataclass.core.base import BaseModel
from .prompt_attributes import PromptAttributes
from ..handlers import FILE_HANDLERS
from ..schema.schema_json import extract_schema_fields_from_json
from ..schema.schema_prompt_builder import SchemaPromptBuilder

logger = logging.getLogger(__name__)

@dataclass
class PromptTemplate(BaseModel):
    type: str
    subtype: str
    prompt_text: str
    prompt_system_use: bool = False
    prompt_system_text: str = "You are a helpful AI Assistant"
    custom_system_prompt_name: Optional[str] = None
    notes: Optional[str] = None
    default_attributes: PromptAttributes = field(default_factory=PromptAttributes)

    def __post_init__(self):
        if isinstance(self.default_attributes, dict):
            logger.debug("PromptTemplate: converting default_attributes from dict.")
            self.default_attributes = PromptAttributes.from_dict(self.default_attributes)

    # Get placeholder methods
    def get_text_placeholders(self) -> list[str]:
        return re.findall(r'<<\s*([\w.-]+)\s*>>', self.prompt_text)

    def get_file_placeholders(self) -> list[str]:
        return re.findall(r'%%\s*(.*?)\s*%%', self.prompt_text)

    def get_multifile_placeholders(self) -> list[str]:
        return re.findall(r'%m%\s*(.*?)\s*%m%', self.prompt_text)

    def get_directory_placeholders(self) -> list[str]:
        return re.findall(r'%d%\s*(.*?)\s*%d%', self.prompt_text)

    def get_output_schema_placeholders(self) -> list[str]:
        return re.findall(r'@@\s*([\w.-]+)\s*@@', self.prompt_text)

    def get_output_prompt_placeholder(self):
        return re.findall(r'\^\^\s*output_fields\s*\^\^', self.prompt_text)

    def get_display_prompt(self) -> str:
        """
        Returns a display-ready version of the prompt:
        - Removes @@schema fields@@
        - Replaces ^^output_fields^^ with a generated instruction section
        """
        text = self.strip_output_schema_placeholders()
        text = self.replace_output_fields_section(text)
        return text

    def get_all_placeholders(self) -> dict:
        return {
            "text": self.get_text_placeholders(),
            "file": self.get_file_placeholders(),
            "multi_file": self.get_multifile_placeholders(),
            "directory": self.get_directory_placeholders(),
            "output": self.get_output_schema_placeholders(),
            "output_prompt": self.get_output_prompt_placeholder()
        }

    # Other Get methods
    def get_formatted_prompt(self, values: Dict[str, str | Path | list[str | Path]]) -> str:
        """
        Applies all placeholder replacements. `values` may map keys to:
          - a str or Path for single-file/text placeholders
          - a list[str|Path] for multi-file placeholders
        """
        formatted = self.prompt_text

        # 1) simple text placeholders
        formatted = self.replace_text_placeholders(values, formatted)

        # 2) single-file placeholders
        formatted = self.replace_file_placeholders(values, formatted)

        # 3) multi-file placeholders
        formatted = self.replace_multifile_placeholders(values, formatted)

        # 4) directory placeholders
        formatted = self.replace_directory_placeholders(values, formatted)

        # 5) ^^output_fields^^ section (if a schema is provided)
        output_pattern = re.compile(r"\^\^\s*output_fields\s*\^\^", re.IGNORECASE)
        if re.search(output_pattern, formatted):
            schema = getattr(self.default_attributes, "response_format", None)
            if isinstance(schema, dict):
                try:
                    fields = extract_schema_fields_from_json(schema)
                    section = SchemaPromptBuilder(fields).generate_prompt_section()
                    formatted = re.sub(output_pattern, section, formatted)
                    logger.debug("✅ Replaced ^^output_fields^^ with schema section.")
                except Exception as e:
                    logger.warning(f"⚠️ Error generating output_fields section: {e}")
            else:
                logger.warning("⚠️ No valid schema found in default_attributes.response_format")

        return formatted

    def get_original_prompt_hash(self) -> str:
        return hashlib.sha256(self.prompt_text.encode('utf-8')).hexdigest()

    # Replace placeholder methods
    def replace_text_placeholders(self,
                                  values: dict[str, str],
                                  prompt_text: Optional[str] = None) -> str:
        """
        Replace << key >> placeholders with string values.

        Contract:
        - Text placeholders are string-only.
        - Non-string values are programmer error and should fail fast.
        """
        prompt_text = prompt_text or self.prompt_text
        for key in self.get_text_placeholders():
            if key not in values:
                continue

            value = values.get(key)
            if value is not None:
                pattern = fr'<<\s*{re.escape(key)}\s*>>'
                prompt_text = re.sub(pattern, value, prompt_text)
        return prompt_text

    def replace_multifile_placeholders(self,
                                       values: dict[str, list[str | Path]],
                                       prompt_text: Optional[str] = None) -> str:
        prompt_text = prompt_text or self.prompt_text
        for key in self.get_multifile_placeholders():
            files = values.get(key, [])
            if not isinstance(files, list):
                continue
            contents = []
            for file in files:
                if isinstance(file, str):
                    file = Path(file)
                handler = FILE_HANDLERS.get(file.suffix.lower())

                # Add explicit tape/file label ONCE
                file_label = f"=== START {file.stem} ==="
                contents.append(file_label)

                if handler:
                    try:
                        contents.append(handler(file))
                    except Exception as e:
                        logger.warning(f"Error in handler for {file}: {e}")
                        contents.append(f"[Error reading file: {file.name}]")
                else:
                    contents.append(f"[Unsupported file type: {file.suffix}]")
            all_content = "\n\n".join(contents)
            pattern = fr'%m%\s*{re.escape(key)}\s*%m%'
            prompt_text = re.sub(pattern, lambda m: all_content, prompt_text)
        return prompt_text

    def replace_file_placeholders(
        self,
        values: dict[str, str | Path | list[str | Path]],
        prompt_text: Optional[str] = None
    ) -> str:
        """
        Replaces each %% key %% with the contents of one or more files.
        Accepts values[key] as:
          - a single str or Path
          - a list[str|Path]
        """
        text = prompt_text or self.prompt_text

        for key in self.get_file_placeholders():
            raw = values.get(key)
            if raw is None:
                continue

            # Normalize to a list
            files: list[Path] = []
            if isinstance(raw, list):
                files = [Path(f) if isinstance(f, str) else f for f in raw]
            else:
                files = [Path(raw)] if isinstance(raw, (str, Path)) else []

            # Read & collect each file’s contents
            contents: list[str] = []
            for path in files:
                handler = FILE_HANDLERS.get(path.suffix.lower())
                if handler:
                    try:
                        contents.append(handler(path))
                    except Exception as e:
                        logger.error(f"Error reading {path}: {e}")
                        contents.append(f"[Error reading file: {path.name}]")
                else:
                    contents.append(f"[Unsupported file type: {path.suffix}]")

            # If we got something, join and replace
            if contents:
                replacement = "\n\n".join(contents)
                pattern = fr'%%\s*{re.escape(key)}\s*%%'
                text = re.sub(pattern, lambda m: replacement, text)

        return text

    def replace_directory_placeholders(
            self,
            values: dict[str, str | Path | list[str | Path]],
            prompt_text: Optional[str] = None
    ) -> str:
        """
        Replaces each %d% key %d% with the combined contents of all files in the directory
        referenced by values[key].

        Behavior matches replace_multifile_placeholders():
        - Adds a label per file: === START <stem> ===
        - Uses FILE_HANDLERS by suffix
        - On handler error: logs + inserts [Error reading file: ...]
        - On unsupported suffix: inserts [Unsupported file type: ...]
        """
        text = prompt_text or self.prompt_text

        for key in self.get_directory_placeholders():
            raw = values.get(key)
            print(f"Raw: {raw}")
            if raw is None:
                continue

            dir_path = Path(raw) if isinstance(raw, str) else raw
            print(f"Directory-path: {dir_path}")
            if not isinstance(dir_path, Path) or not dir_path.exists() or not dir_path.is_dir():
                logger.warning(f"Directory placeholder '{key}' is not a valid directory: {raw}")
                continue

            contents: list[str] = []
            try:
                files = sorted(p for p in dir_path.iterdir() if p.is_file())
            except Exception as e:
                logger.warning(f"Error scanning directory {dir_path}: {e}")
                files = []

            for file in files:
                handler = FILE_HANDLERS.get(file.suffix.lower())

                file_label = f"=== START {file.stem} ==="
                contents.append(file_label)

                if handler:
                    try:
                        contents.append(handler(file))
                    except Exception as e:
                        logger.warning(f"Error in handler for {file}: {e}")
                        contents.append(f"[Error reading file: {file.name}]")
                else:
                    contents.append(f"[Unsupported file type: {file.suffix}]")

            all_content = "\n\n".join(contents)
            pattern = fr'%d%\s*{re.escape(key)}\s*%d%'
            text = re.sub(pattern, lambda m: all_content, text)

        return text


    def replace_output_fields_section(self, prompt_text: Optional[str] = None) -> str:
        """
        Replace ^^ output_fields ^^ with a text description generated from the response_format schema.
        """
        text = prompt_text or self.prompt_text
        output_pattern = re.compile(r"\^\^\s*output_fields\s*\^\^", re.IGNORECASE)

        if not re.search(output_pattern, text):
            return text

        schema = getattr(self.default_attributes, "response_format", None)
        if not isinstance(schema, dict):
            logger.warning("⚠️ No valid schema found in default_attributes.response_format")
            return text

        try:
            fields = extract_schema_fields_from_json(schema)
            builder = SchemaPromptBuilder(fields)
            section = builder.generate_prompt_section()
            text = re.sub(output_pattern, section, text)
            logger.debug("✅ Replaced ^^ output_fields ^^ with schema section.")
        except Exception as e:
            logger.warning(f"⚠️ Error generating output_fields section: {e}")

        return text

    def strip_output_schema_placeholders(self, prompt_text: Optional[str] = None) -> str:
        """
        Remove all @@ placeholder fields from the prompt.
        These are only used to define schema output fields.
        """
        text = prompt_text or self.prompt_text
        return re.sub(r'@@\s*[\w.-]+\s*@@', '', text)

    def fill_placeholders(self, values: dict[str, str | Path | list[str | Path]], prompt_text: Optional[str] = None) -> str:
        """
        Applies file and text placeholder replacements using the given values.
        Returns a fully substituted prompt.
        """
        text = prompt_text or self.prompt_text
        text = self.replace_text_placeholders(values, text)
        text = self.replace_file_placeholders(values, text)
        text = self.replace_multifile_placeholders(values, text)
        text = self.replace_directory_placeholders(values, text)
        return text

     # Load methods
    def load_file_values(self, file_path: Path) -> Dict[str, str]:
        file_values = {}
        name = file_path.stem
        if file_path.exists() and file_path.is_file():
            with file_path.open("r", encoding="utf-8") as f:
                file_values[name] = f.read().strip()
        else:
            file_values[name] = f"[ERROR: {file_path.name} not found]"
        return file_values

    # TESTING

    def get_output_fields(self):
        schema = (self.default_attributes.response_format or {}).get("json_schema", {})
        fields = schema.get("schema", {}).get("properties", {})
        return list(fields.keys())

    ## REMOVE? ##
    # Generate prompt method
    def generate_prompt(self, prompt_text: str) -> list[str]:
        self.prompt_text = prompt_text
        return self.get_text_placeholders()
