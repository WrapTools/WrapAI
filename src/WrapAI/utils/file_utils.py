# utils/file_utils.py

# IN DEVELOPMENT

from pathlib import Path
from typing import Union, Optional
import logging

from ..handlers import FILE_HANDLERS

logger = logging.getLogger(__name__)

def get_formatted_file_contents(
    input_file: Union[str, Path, None] = None,
    input_files: Union[list[str | Path], None] = None
) -> str:
    """
    Load and format contents from one or many files, returning a single formatted string.
    """
    paths: list[Path] = []

    # Normalize to list of Path objects
    if input_files:
        if isinstance(input_files, (str, Path)):
            paths = [Path(input_files)]
        else:
            paths = [Path(p) for p in input_files]
    elif input_file:
        paths = [Path(input_file)]

    parts = []
    for path in paths:
        handler = FILE_HANDLERS.get(path.suffix.lower())
        try:
            if handler:
                text = handler(path)
            else:
                text = f"[Unsupported file type: {path.suffix}]"
        except Exception as e:
            logger.warning(f"Error loading {path}: {e}")
            text = f"[Error reading {path.name}]"
        parts.append(f"===== {path.name} =====\n{text}")

    return "\n\n".join(parts)
