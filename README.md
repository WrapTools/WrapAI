# WrapAI

![Status](https://img.shields.io/badge/status-beta-orange)
![Python](https://img.shields.io/badge/python-3.x-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
![Intended Use](https://img.shields.io/badge/intended_use-personal%20%2F%20reuse-lightgrey)

Lightweight Python wrapper for running text and chat prompts with
Venice and OpenAI, including prompt templates, structured outputs,
and conversation memory.

## Highlights

- Prompt templates with placeholders and variable substitution
- Unified interface for Venice and OpenAI providers
- Structured response schemas with automatic parsing
- Conversation memory with token limits and summarization
- Extensible file handler system (TXT, PDF, and custom types)

## Overview

WrapAI provides a reusable prompt framework for running AI requests
in Python projects. It supports both single text prompts and
multi-message chat prompts with optional conversation memory.

The library includes a prompt template system with placeholder
replacement, schema-based structured responses, and runtime prompt
execution helpers. Provider abstractions allow the same prompt logic
to run against different AI APIs such as Venice and OpenAI.

WrapAI is designed to stay lightweight and composable. It relies on
small supporting libraries such as WrapDataclass for structured data
models and WrapEmit for runtime progress reporting.

## Requirements

- Python 3.x
- API key for Venice or OpenAI

## Installation

Requires [uv](https://github.com/astral-sh/uv).

```bash
uv sync
```

## Quick Start

### CLI

Run a simple text prompt using the provider helper.

```python
from WrapAI import open_provider

provider = open_provider(
    provider="venice",
    api_key="YOUR_API_KEY",
    model="venice-uncensored"
)

response = provider.text("What is the capital of Italy?")
print(response.response)
```

The helper automatically selects the correct provider implementation
(Venice or OpenAI) while keeping calling code simple.

Advanced usage can interact directly with the lower-level prompt
classes inside `WrapAI.prompt`.

### Chat

Conversation prompts with memory support.

```python
from WrapAI import open_provider

chat = open_provider(
    provider="venice",
    api_key="YOUR_API_KEY",
    model="venice-uncensored"
)

chat.user("Explain what recursion is.")
chat.user("Give a short Python example.")

response = chat.run()
print(response.response)
```

## Prompt Templates

WrapAI supports reusable prompt templates with placeholder
substitution. Placeholders are replaced at runtime before the prompt
is sent to the model.

Common placeholders include:

| Placeholder         | Purpose                           |
| ------------------- | --------------------------------- |
| `<< text >>`        | Text input provided by the caller |
| `%% file %%`        | Replace with contents of a file   |
| `%m% files %m%`     | Insert multiple files             |
| `%d% directory %d%` | Insert files from a directory     |

Some placeholders are used when generating structured outputs:

| Placeholder           | Purpose                                      |
| --------------------- | -------------------------------------------- |
| `@@ schema_fields @@` | Defines fields used for JSON schema output   |
| `^^ output_fields ^^` | Generates instructions describing the schema |

Example prompt template:

```
Summarize the following document.

<< text >>

Return the result as JSON using these fields:

@@ schema_fields @@
^^ output_fields ^^
```

Templates can be executed directly or managed through higher-level
prompt management systems built on top of WrapAI.

## Examples

See the [`examples/public/`](./examples/public/) directory for runnable examples.

The examples include a single script demonstrating most major
WrapAI capabilities including:

- Stateless prompts
- Streaming responses
- Chat with conversation memory
- Prompt libraries
- Placeholder substitution
- Model inspection utilities

Run the example script to explore the available features:

```bash
uv run examples/public/example_ai_HELPERS.py
```

## Dependencies
| Library                                                     | Purpose                                                  |
|-------------------------------------------------------------|----------------------------------------------------------|
| [WrapDataclass](https://github.com/WrapTools/WrapDataclass) | Dataclass serialization and model utilities              |
| [WrapEmit](https://github.com/WrapTools/WrapEmit)           | Runtime event emission and logging                       |
| WrapCapPDF                                                  | Optional PDF file extraction support (not yet published) |

## Intended Audience

Built for personal use across a growing collection of Python
projects and experiments. Shared publicly as-is — functional
and reused regularly, but not hardened or reviewed for
general-purpose production use.

No guarantees, but feel free to use, fork, or adapt it.
Feedback welcome.

## License

MIT — see [LICENSE](./LICENSE).
