# handlers/base_handlers.py

from pathlib import Path

def register():
    return {
        ".txt": lambda path: path.read_text(encoding="utf-8").strip(),
        ".py": lambda path: path.read_text(encoding="utf-8").strip(),
        ".md": lambda path: path.read_text(encoding="utf-8").strip(),
        ".json": lambda path: path.read_text(encoding="utf-8").strip(),
        ".yaml": lambda path: path.read_text(encoding="utf-8").strip(),
        ".yml": lambda path: path.read_text(encoding="utf-8").strip(),
        ".toml": lambda path: path.read_text(encoding="utf-8").strip(),
        ".csv": lambda path: path.read_text(encoding="utf-8").strip(),
        ".tsv": lambda path: path.read_text(encoding="utf-8").strip(),
        ".ini": lambda path: path.read_text(encoding="utf-8").strip(),
        ".log": lambda path: path.read_text(encoding="utf-8").strip(),
        ".rst": lambda path: path.read_text(encoding="utf-8").strip(),
        ".ged": lambda path: path.read_text(encoding="utf-8").strip(),
    }
