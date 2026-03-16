# schema/schema_json.py

import json
from typing import List, Dict, Any, Optional, Union, Literal
from dataclasses import dataclass
import logging

# Logger Configuration
logger = logging.getLogger(__name__)


@dataclass
class SchemaField:
    name: str
    type: Literal["string", "number", "integer", "boolean", "array", "enum", "const"]
    required: bool = True
    description: Optional[str] = None

    # Optional for specific types
    item_type: Optional[str] = None       # for arrays
    enum_values: Optional[List[str]] = None  # for enums
    value: Optional[Union[str, int, float, bool]] = None  # for consts


class SchemaBuilder:
    """Helper class to build JSON schema structures for API response formats."""

    def __init__(self, schema_name: str):
        self.schema_name = schema_name
        self.properties = {}
        self.required = []

    def add_string_property(self, name: str, required: bool = True, description: str = None):
        """Add a string property to the schema."""
        prop = {"type": "string"}
        if description:
            prop["description"] = description

        self.properties[name] = prop
        if required:
            self.required.append(name)
        return self

    def add_number_property(self, name: str, required: bool = True, description: str = None):
        """Add a number property to the schema."""
        prop = {"type": "number"}
        if description:
            prop["description"] = description

        self.properties[name] = prop
        if required:
            self.required.append(name)
        return self

    def add_integer_property(self, name: str, required: bool = True, description: str = None):
        """Add an integer property to the schema."""
        prop = {"type": "integer"}
        if description:
            prop["description"] = description

        self.properties[name] = prop
        if required:
            self.required.append(name)
        return self

    def add_array_property(self, name: str, item_type: str = "string", required: bool = True, description: str = None):
        """Add an array property to the schema."""
        prop = {
            "type": "array",
            "items": {"type": item_type}
        }
        if description:
            prop["description"] = description

        self.properties[name] = prop
        if required:
            self.required.append(name)
        return self

    def add_object_property(self, name: str, properties: Dict[str, Dict], required: List[str] = None,
                           required_in_schema: bool = True, description: str = None):
        """Add a nested object property to the schema."""
        prop = {
            "type": "object",
            "properties": properties
        }
        if required:
            prop["required"] = required
        if description:
            prop["description"] = description

        self.properties[name] = prop
        if required_in_schema:
            self.required.append(name)
        return self

    def add_boolean_property(self, name: str, required: bool = True, description: str = None):
        """Add a boolean property (true/false) to the schema."""
        prop = {"type": "boolean"}
        if description:
            prop["description"] = description

        self.properties[name] = prop
        if required:
            self.required.append(name)
        return self

    def add_enum_property(self, name: str, enum_values: List[str], required: bool = True, description: str = None):
        """Add a string property with an enum constraint."""
        prop = {
            "type": "string",
            "enum": enum_values
        }
        if description:
            prop["description"] = description

        self.properties[name] = prop
        if required:
            self.required.append(name)
        return self

    def add_const_property(self, name: str, value: Union[str, int, float, bool], description: str = None):
        """Add a constant-valued property to the schema."""
        prop = {"const": value}
        if isinstance(value, str):
            prop["type"] = "string"
        elif isinstance(value, int):
            prop["type"] = "integer"
        elif isinstance(value, float):
            prop["type"] = "number"
        elif isinstance(value, bool):
            prop["type"] = "boolean"

        if description:
            prop["description"] = description

        self.properties[name] = prop
        self.required.append(name)
        return self

    def add_optional_property(self, name: str, schema: Dict[str, Any]):
        """Add a fully-formed optional property schema."""
        self.properties[name] = schema
        return self

    def add_nested_schema_property(self, name: str, nested: "SchemaBuilder", required: bool = True,
                                   description: str = None):
        """Add a nested SchemaBuilder object as a sub-property."""
        prop = {
            "type": "object",
            "properties": nested.properties
        }
        if nested.required:
            prop["required"] = nested.required
        if description:
            prop["description"] = description

        self.properties[name] = prop
        if required:
            self.required.append(name)
        return self

    def add_field(self, field: SchemaField):
        if field.type == "string":
            self.add_string_property(field.name, field.required, field.description)
        elif field.type == "number":
            self.add_number_property(field.name, field.required, field.description)
        elif field.type == "integer":
            self.add_integer_property(field.name, field.required, field.description)
        elif field.type == "boolean":
            self.add_boolean_property(field.name, field.required, field.description)
        elif field.type == "array":
            self.add_array_property(field.name, item_type=field.item_type or "string", required=field.required,
                                    description=field.description)
        elif field.type == "enum":
            self.add_enum_property(field.name, field.enum_values or [], field.required, field.description)
        elif field.type == "const":
            self.add_const_property(field.name, field.value, field.description)
        else:
            raise ValueError(f"Unsupported type: {field.type}")
        return self

    def build(self) -> Dict[str, Any]:
        """Build the complete JSON schema structure."""
        schema = {
            "type": "json_schema",
            "json_schema": {
                "name": self.schema_name,
                "schema": {
                    "type": "object",
                    "properties": self.properties
                }
            }
        }

        if self.required:
            schema["json_schema"]["schema"]["required"] = self.required

        return schema

    def to_json(self, indent: int = 4) -> str:
        """Convert the schema to a JSON string."""
        return json.dumps(self.build(), indent=indent)

    def print_json(self):
        """Print the schema as formatted JSON."""
        print(self.to_json())

    def clear_properties(self):
        """Clear all properties and required fields from the schema."""
        self.properties.clear()
        self.required.clear()
        return self

    def load_properties(self, fields: List["SchemaField"]):
        for field in fields:
            if field.type == "string":
                self.add_string_property(field.name, field.required, field.description)
            elif field.type == "number":
                self.add_number_property(field.name, field.required, field.description)
            elif field.type == "integer":
                self.add_integer_property(field.name, field.required, field.description)
            elif field.type == "boolean":
                self.add_boolean_property(field.name, field.required, field.description)
            elif field.type == "array":
                self.add_array_property(field.name, item_type=field.item_type or "string", required=field.required,
                                        description=field.description)
            elif field.type == "enum":
                if not field.enum_values:
                    raise ValueError(f"Missing enum_values for {field.name}")
                self.add_enum_property(field.name, field.enum_values, field.required, field.description)
            elif field.type == "const":
                if field.value is None:
                    raise ValueError(f"Missing value for const {field.name}")
                self.add_const_property(field.name, field.value, field.description)
            else:
                raise ValueError(f"Unsupported type: {field.type}")
        return self


def extract_schema_fields_from_json(schema_json: dict) -> List[SchemaField]:
    schema = schema_json["json_schema"]["schema"]
    required_fields = set(schema.get("required", []))
    fields = []

    for name, prop in schema["properties"].items():
        field_type = prop.get("type")
        description = prop.get("description")
        is_required = name in required_fields

        # Handle arrays
        if field_type == "array":
            item_type = prop.get("items", {}).get("type", "string")
            fields.append(SchemaField(name=name, type="array", required=is_required,
                                      description=description, item_type=item_type))

        # Handle enums
        elif "enum" in prop:
            fields.append(SchemaField(name=name, type="enum", required=is_required,
                                      description=description, enum_values=prop["enum"]))

        # Handle const
        elif "const" in prop:
            value = prop["const"]
            inferred_type = type(value).__name__
            fields.append(SchemaField(name=name, type="const", required=True,
                                      description=description, value=value))

        # Simple types
        else:
            fields.append(SchemaField(name=name, type=field_type, required=is_required,
                                      description=description))
    return fields

def reconcile_schema_fields(
    field_names: List[str],
    schema_json: Optional[dict] = None,
    schema_name: str = "ReconciledSchema",
    default_type: str = "string",
    default_required: bool = True,
    return_builder: bool = False
) -> Union[dict, SchemaBuilder]:
    """
    Reconcile schema fields based on the given field names.

    If return_builder is True, returns a SchemaBuilder instance.
    Otherwise, returns the raw schema JSON dict.
    """
    # Start from existing schema or blank
    if schema_json is None:
        schema_json = {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }

    schema = schema_json["json_schema"]["schema"]
    properties = schema.get("properties", {})

    updated_properties = {}
    updated_required = []

    for name in field_names:
        if name in properties:
            updated_properties[name] = properties[name]
        else:
            updated_properties[name] = {
                "type": default_type,
                "description": f"Auto-added field for '{name}'"
            }
        if default_required:
            updated_required.append(name)

    # Update schema dict
    schema["properties"] = updated_properties
    schema["required"] = updated_required
    schema_json["json_schema"]["schema"] = schema

    # Optional: return SchemaBuilder instance
    if return_builder:
        builder = SchemaBuilder(schema_json["json_schema"]["name"])
        builder.properties = updated_properties
        builder.required = updated_required
        return builder

    return schema_json
