# utils/token_char.py

import tiktoken
import logging

# Logger Configuration
logger = logging.getLogger(__name__)


def count_characters_and_tokens(text, model='gpt-3.5-turbo'):
    """Returns the character count and token count of the input text."""
    # Character count
    char_count = len(text)

    # Token count using tiktoken
    try:
        # Attempt to get encoding for the specified model
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to a default encoding if model-specific encoding is unavailable
        logger.error(f"Model '{model}' not found. Using 'gpt-3.5-turbo' encoding as a fallback.")
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    token_count = len(encoding.encode(text))
    return char_count, token_count

def split_text_to_token_chunks(text: str, max_tokens: int, model: str = 'gpt-3.5-turbo') -> list[str]:
    """Split `text` into chunks each ≤ max_tokens tokens for the given model."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.error(f"Model '{model}' not found. Using 'gpt-3.5-turbo' encoding as a fallback.")
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(text)
    chunks: list[str] = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i : i + max_tokens]
        chunks.append(encoding.decode(chunk_tokens))
    return chunks
