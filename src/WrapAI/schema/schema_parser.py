# schema/schema_parser.py

from typing import Any, Optional
import logging

from .schema_json import extract_schema_fields_from_json

logger = logging.getLogger(__name__)

def parse_response_with_schema(
    response_json: dict,
    schema_json: dict,
    include_missing_optionals: bool = False
) -> dict:
    """
    Parse a response JSON object using a schema definition and return a typed dict.
    Optionally include missing optional fields as `None`.
    """
    parsed = {}
    fields = extract_schema_fields_from_json(schema_json)

    for field in fields:
        value = response_json.get(field.name)

        if value is None:
            if field.required:
                raise ValueError(f"Missing required field: {field.name}")
            elif include_missing_optionals:
                parsed[field.name] = None
            continue

        # Validate field type
        if not _validate_field_type(field, value):
            raise ValueError(f"Field '{field.name}' validation failed for type '{field.type}'")

        parsed[field.name] = value

    return parsed

def format_parsed_output(
    parsed: dict,
    title: Optional[str] = None,
    format_type: str = "text"
) -> str:
    """Format parsed data as text or markdown."""
    if format_type.lower() == "markdown":
        return _format_as_markdown(parsed, title)
    return _format_as_text(parsed, title)

def _validate_field_type(field, value: Any) -> bool:
    """Validate field value against expected type."""
    validators = {
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int),
        "number": lambda v: isinstance(v, (int, float)),
        "boolean": lambda v: isinstance(v, bool),
        "enum": lambda v: v in field.enum_values,
        "const": lambda v: v == field.value
    }

    validator = validators.get(field.type)
    return validator(value) if validator else True

def _format_as_markdown(parsed: dict, title: Optional[str] = None) -> str:
    """Convert parsed dict to markdown format."""
    output: list[str] = []  # Explicit type annotation
    if title:
        output.append(f"# {title}\n")

    for key, value in parsed.items():
        if not _has_visible_content(value):
            continue

        header = key.replace("_", " ").capitalize()
        output.append(f"## {header}")

        if isinstance(value, list):
            output.extend(f"- {item}" for item in value)
        else:
            output.append(str(value))

    return "\n\n".join(output)


def _format_as_text(parsed: dict, title: Optional[str] = None) -> str:
    """Convert parsed dict to plain text format."""
    lines: list[str] = []  # Explicit type annotation

    if title:
        lines.extend([title, "=" * len(title), ""])

    for key, value in parsed.items():
        if not _has_visible_content(value):
            continue

        lines.append(f"=== {key.upper()} ===")

        if isinstance(value, list):
            lines.extend(f"- {item}" for item in value if value)
        else:
            lines.append(str(value).strip())

        lines.append("")

    return "\n".join(lines)

def _has_visible_content(value: Any) -> bool:
    """Check if value has meaningful content."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().lower() != "none"
    if isinstance(value, list):
        return bool(value)
    return True


# # schema/schema_parser.py
#
# from typing import Any, Optional, Literal, Union
# import logging
# from dataclasses import dataclass
#
# from .schema_json import extract_schema_fields_from_json
#
# logger = logging.getLogger(__name__)
#
# @dataclass
# class ParseConfig:
#     """Configuration for parsing behavior."""
#     include_missing_optionals: bool = False
#     strict_validation: bool = True
#
# class SchemaParser:
#     """Main parser class for schema-based response parsing."""
#
#     def __init__(self, config: Optional[ParseConfig] = None):
#         self.config = config or ParseConfig()
#
#     def parse_response(self, response_json: dict, schema_json: dict) -> dict:
#         """Parse response JSON using schema definition."""
#         parsed = {}
#         fields = extract_schema_fields_from_json(schema_json)
#
#         for field in fields:
#             value = response_json.get(field.name)
#
#             if value is None:
#                 self._handle_missing_field(field, parsed)
#                 continue
#
#             self._validate_and_assign(field, value, parsed)
#
#         return parsed
#
#     def _handle_missing_field(self, field, parsed: dict) -> None:
#         """Handle missing field based on requirements."""
#         if field.required:
#             raise ValueError(f"Missing required field: {field.name}")
#         elif self.config.include_missing_optionals:
#             parsed[field.name] = None
#
#     def _validate_and_assign(self, field, value: Any, parsed: dict) -> None:
#         """Validate field value and assign to parsed dict."""
#         validators = {
#             "array": lambda v: isinstance(v, list),
#             "string": lambda v: isinstance(v, str),
#             "integer": lambda v: isinstance(v, int),
#             "number": lambda v: isinstance(v, (int, float)),
#             "boolean": lambda v: isinstance(v, bool),
#             "enum": lambda v: v in field.enum_values,
#             "const": lambda v: v == field.value
#         }
#
#         validator = validators.get(field.type)
#         if validator and not validator(value):
#             raise ValueError(f"Field '{field.name}' validation failed for type '{field.type}'")
#
#         parsed[field.name] = value
#
# class ResponseFormatter:
#     """Handles formatting of parsed responses."""
#
#     @staticmethod
#     def format_as_markdown(parsed: dict, title: Optional[str] = None) -> str:
#         """Convert parsed dict to markdown format."""
#         output = []
#         if title:
#             output.append(f"# {title}\n")
#
#         for key, value in parsed.items():
#             if not ResponseFormatter._has_visible_content(value):
#                 continue
#
#             header = key.replace("_", " ").capitalize()
#             output.append(f"## {header}")
#
#             if isinstance(value, list):
#                 output.extend(f"- {item}" for item in value)
#             else:
#                 output.append(str(value))
#
#         return "\n\n".join(output)
#
#     @staticmethod
#     def format_as_text(parsed: dict, title: Optional[str] = None) -> str:
#         """Convert parsed dict to plain text format."""
#         lines = []
#
#         if title:
#             lines.extend([title, "=" * len(title), ""])
#
#         for key, value in parsed.items():
#             if not ResponseFormatter._has_visible_content(value):
#                 continue
#
#             lines.append(f"=== {key.upper()} ===")
#
#             if isinstance(value, list):
#                 lines.extend(f"- {item}" for item in value if value)
#             else:
#                 lines.append(str(value).strip())
#
#             lines.append("")
#
#         return "\n".join(lines)
#
#     @staticmethod
#     def format_output(
#         parsed: dict,
#         title: Optional[str] = None,
#         format_type: Union[str, Literal["text", "markdown"]] = "text"
#     ) -> str:
#         """Format parsed data based on output type."""
#         # Normalize format_type to ensure it's valid
#         normalized_format = format_type.lower() if isinstance(format_type, str) else format_type
#         if normalized_format not in ("text", "markdown"):
#             normalized_format = "text"
#
#         if normalized_format == "markdown":
#             return ResponseFormatter.format_as_markdown(parsed, title)
#         return ResponseFormatter.format_as_text(parsed, title)
#
#     @staticmethod
#     def _has_visible_content(value: Any) -> bool:
#         """Check if value has meaningful content."""
#         if value is None:
#             return False
#         if isinstance(value, str):
#             return bool(value.strip()) and value.strip().lower() != "none"
#         if isinstance(value, list):
#             return bool(value)
#         return True
#
# # Convenience functions for backward compatibility
# def parse_response_with_schema(
#     response_json: dict,
#     schema_json: dict,
#     include_missing_optionals: bool = False
# ) -> dict:
#     """Legacy function - use SchemaParser class instead."""
#     config = ParseConfig(include_missing_optionals=include_missing_optionals)
#     parser = SchemaParser(config)
#     return parser.parse_response(response_json, schema_json)
#
# def format_parsed_output(
#     parsed: dict,
#     title: Optional[str] = None,
#     format_type: str = "text"
# ) -> str:
#     """Legacy function - use ResponseFormatter class instead."""
#     return ResponseFormatter.format_output(parsed, title, format_type)




# # schema/schema_parser.py
#
# from typing import Any, Optional
# import logging
#
# # Logger Configuration
# logger = logging.getLogger(__name__)
#
# from .schema_json import extract_schema_fields_from_json
#
#
# def parse_response_with_schema(
#     response_json: dict,
#     schema_json: dict,
#     include_missing_optionals: bool = False
# ) -> dict:
#     """
#     Parse a response JSON object using a schema definition and return a typed dict.
#     Optionally include missing optional fields as `None`.
#
#     :param response_json: The raw JSON dictionary returned by the AI or API.
#     :param schema_json: The schema used to validate and extract expected fields.
#     :param include_missing_optionals: If True, include missing optional fields with value None.
#     :return: A new dict matching the schema.
#     """
#     parsed = {}
#     fields = extract_schema_fields_from_json(schema_json)
#
#     for field in fields:
#         value = response_json.get(field.name)
#
#         # if field.required and value is None:
#         #     raise ValueError(f"Missing required field: {field.name}")
#
#         if value is None:
#             if field.required:
#                 raise ValueError(f"Missing required field: {field.name}")
#             elif include_missing_optionals:
#                 parsed[field.name] = None
#             continue
#
#         expected_type = field.type
#         if expected_type == "array":
#             if not isinstance(value, list):
#                 raise ValueError(f"Field '{field.name}' should be a list.")
#         elif expected_type == "string":
#             if not isinstance(value, str):
#                 raise ValueError(f"Field '{field.name}' should be a string.")
#         elif expected_type == "integer":
#             if not isinstance(value, int):
#                 raise ValueError(f"Field '{field.name}' should be an integer.")
#         elif expected_type == "number":
#             if not isinstance(value, (int, float)):
#                 raise ValueError(f"Field '{field.name}' should be a number.")
#         elif expected_type == "boolean":
#             if not isinstance(value, bool):
#                 raise ValueError(f"Field '{field.name}' should be a boolean.")
#         elif expected_type == "enum":
#             if value not in field.enum_values:
#                 raise ValueError(f"Invalid value '{value}' for enum field '{field.name}'.")
#         elif expected_type == "const":
#             if value != field.value:
#                 raise ValueError(f"Field '{field.name}' must be '{field.value}'.")
#
#         parsed[field.name] = value
#
#     return parsed
#
# def format_parsed_as_markdown(parsed: dict, title: str = None) -> str:
#     """
#     Given a parsed response dict (conforming to a schema), convert it to markdown.
#
#     :param parsed: Parsed dictionary matching schema
#     :param title: Optional title to include at the top
#     :return: Markdown-formatted string
#     """
#     output = []
#     if title:
#         output.append(f"# {title}\n")
#
#     for key, value in parsed.items():
#         if value is None or (isinstance(value, str) and value.strip().lower() in {"none", ""}):
#             continue
#
#         header = key.replace("_", " ").capitalize()
#         output.append(f"## {header}")
#         if isinstance(value, list):
#             for item in value:
#                 output.append(f"- {item}")
#         else:
#             output.append(str(value))
#
#     return "\n\n".join(output)
#
# def format_parsed_as_text(parsed: dict, title: str | None = None) -> str:
#     """
#     Convert a parsed dict into plain text with delimited sections.
#     Optional title can be provided for top heading.
#     """
#     lines: list[str] = []
#
#     if title:
#         lines.append(f"{title}")
#         lines.append("=" * len(title))
#         lines.append("")
#
#     for key, value in parsed.items():
#         if value is None or (isinstance(value, str) and not value.strip()):
#             continue  # Skip empty entries
#
#         lines.append(f"=== {key.upper()} ===")
#
#         if isinstance(value, list):
#             if not value:
#                 continue
#             for item in value:
#                 lines.append(f"- {item}")
#         else:
#             lines.append(str(value).strip())
#
#         lines.append("")
#
#     return "\n".join(lines)
#
# def format_parsed_output(
#     parsed: dict,
#     title: Optional[str] = None,
#     format_type: str = "text"
# ) -> str:
#     """
#     Format parsed data based on output type.
#     :param parsed: Parsed schema result
#     :param title: Optional title
#     :param format_type: 'text' or 'markdown'
#     """
#     if format_type == "markdown":
#         return format_parsed_as_markdown(parsed, title)
#     return format_parsed_as_text(parsed, title)
#
#
# def _has_visible_content(value: Any) -> bool:
#     """Returns True if the value is meaningfully non-empty."""
#     if value is None:
#         return False
#     if isinstance(value, str):
#         return bool(value.strip()) and value.strip().lower() != "none"
#     if isinstance(value, list):
#         return bool(value)
#     return True
