# WrapAI Examples

This directory contains runnable examples demonstrating common
WrapAI workflows.

The primary example script covers most major capabilities of the
library. Instead of many small examples, WrapAI uses a single
script that demonstrates the full workflow in one place.

## Example Script

example_ai_HELPERS.py

This script demonstrates:

1. Stateless prompts
2. Direct provider usage
3. Streaming responses
4. Chat with conversation memory
5. Streaming chat
6. Provider-specific options
7. Prompt libraries
8. Placeholder substitution
9. Model inspection utilities
10. Prompt preview tools
11. Account information inspection (Venice)

Most users should start by simply running the script and modifying
the prompts or provider configuration.

## Running the Example

From the repository root:

```bash
uv sync
uv run examples/public/example_ai_HELPERS.py
````

## Provider Configuration

Inside the script you can switch providers by uncommenting
the relevant configuration block.

Example:

```python
PROVIDER = "Venice"
MODEL    = "llama-3.3-70b"
API_KEY  = "VENICE_API_KEY"
```

or

```python
PROVIDER = "OpenAI"
MODEL    = "gpt-4o-mini"
API_KEY  = "OPENAI_API_KEY"
```

## Environment Setup

Create a `.env` file based on `.env_template` and add your API keys.
Example:
```
VENICE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

Alternatively, you can set API keys directly inside the example
script by modifying the `API_KEY` value in the provider
configuration block.

The example scripts will read these values when running.

## Runtime Data
Example scripts may generate runtime data or temporary output files.
These are local artifacts and are not included in the repository.
