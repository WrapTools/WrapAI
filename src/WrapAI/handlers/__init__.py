# handlers/__init__.py

import importlib
import logging
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

FILE_HANDLERS: dict[str, Callable[[Path], str]] = {}

# Always register base handlers
from . import base_handlers
FILE_HANDLERS.update(base_handlers.register())

logger.debug(f"📦 Current package context: {__package__}")

# Discover and register optional handlers
optional_modules = [
    __package__ + ".pdf_handler",  # auto-expand to 'WrapAI.handlers.pdf_handler'
    # Add more as needed
]

for module_name in optional_modules:
    try:
        mod = importlib.import_module(module_name)
        new_handlers = mod.register()
        FILE_HANDLERS.update(new_handlers)
        logger.debug(f"Registered handlers from {module_name}: {list(new_handlers)}")
    except Exception as e:
        logger.debug(f"Optional handler not loaded from {module_name}: {e}")

# After all handlers registered
logger.info(f"📦 Final registered FILE_HANDLERS: {list(FILE_HANDLERS.keys())}")
