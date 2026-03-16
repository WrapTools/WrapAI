# utils/json.py
"""
Utilities for formatting prompt templates.

Includes:
- `DataclassJSONEncoder`: Serializes dataclass instances to JSON-friendly dicts.
"""

import json
from dataclasses import asdict, is_dataclass
import logging

# Logger Configuration
logger = logging.getLogger(__name__)

class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        return super().default(obj)
