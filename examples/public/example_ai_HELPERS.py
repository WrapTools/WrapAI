# examples/public/example_ai_HELPERS.py
"""
WrapAI — single example file covering all major patterns.
Supports both Venice and OpenAI providers.

Switch providers by uncommenting the relevant block below.
"""

from WrapAI import open_provider, inspect
from WrapAI.ai_helper import (
    make_ai, send, stream, chat, stream_chat,
    send_from_library, list_models, count_tokens,
    set_defaults
)

# ---------------------------------------------------------------------------
# Provider configuration — uncomment one block
# ---------------------------------------------------------------------------

# --- Venice (default — cost effective for development) ---
PROVIDER = "Venice"
MODEL    = "llama-3.3-70b"
API_KEY  = "VENICE_API_KEY"

# --- OpenAI ---
# PROVIDER = "OpenAI"
# MODEL    = "gpt-4o-mini"
# API_KEY  = "OPENAI_API_KEY"

LIBRARY = "prompts.json"

# Apply provider choice to all helper functions
set_defaults(provider=PROVIDER, model=MODEL, api_key=API_KEY)

# ---------------------------------------------------------------------------
# 1. Stateless send — no args needed (uses defaults set above)
# ---------------------------------------------------------------------------
print("=== 1. Stateless send (helper) ===")
print(send("What is the capital of France?"))

# ---------------------------------------------------------------------------
# 2. Stateless send — direct open_provider usage
# ---------------------------------------------------------------------------
print("\n=== 2. Stateless send (direct) ===")
ai = open_provider(provider=PROVIDER, model=MODEL, api_key=API_KEY)
ai.set_options(max_completion_tokens=500)
print(ai.send_text_prompt("Explain gravity in one sentence."))

# ---------------------------------------------------------------------------
# 3. Streaming — stateless, no args needed
# ---------------------------------------------------------------------------
print("\n=== 3. Streaming (helper) ===")
stream("Write a haiku about the ocean.")

# ---------------------------------------------------------------------------
# 4. Stateful chat with memory
# ---------------------------------------------------------------------------
print("\n=== 4. Stateful chat ===")
ai_chat = make_ai()
ai_chat.set_system_prompt("You are a concise assistant who answers in bullet points.")

print(chat(ai_chat, "Name three planets."))
print(chat(ai_chat, "Which of those is largest?"))   # memory active
print(chat(ai_chat, "What is its diameter?"))         # still in context

summary = ai_chat.summarize_chat_memory()
print(f"\nMemory summary: {summary}")
ai_chat.clear_chat_memory()

# ---------------------------------------------------------------------------
# 5. Streaming chat with memory
# ---------------------------------------------------------------------------
print("\n=== 5. Streaming chat ===")
ai_stream = make_ai()
stream_chat(ai_stream, "Tell me a short story about a robot.")
stream_chat(ai_stream, "Give it a happier ending.")   # memory active

# ---------------------------------------------------------------------------
# 6. Venice-specific options — skipped for OpenAI
# ---------------------------------------------------------------------------
if PROVIDER == "Venice":
    print("\n=== 6. Venice options (web search) ===")
    ai_venice = open_provider(provider=PROVIDER, model=MODEL, api_key=API_KEY)
    ai_venice.set_options(venice_options={"enable_web_search": "on"})
    print(ai_venice.send_text_prompt("What happened in the news today?"))
else:
    print("\n=== 6. Venice options (skipped — Venice only) ===")

# ---------------------------------------------------------------------------
# 7a. Prompt library — stateless
# ---------------------------------------------------------------------------
print("\n=== 7a. Library prompt (stateless) ===")
result = send_from_library(
    library_path=LIBRARY,
    key="summarize",
    values={"text": "Artificial intelligence is transforming every industry..."}
)
print(result)

# ---------------------------------------------------------------------------
# 7b. Library prompt with <<placeholders>> — stateless
# ---------------------------------------------------------------------------
print("\n=== 7b. Library prompt with placeholders (stateless) ===")

# Assumes prompts.json has a prompt with key "summarize" containing:
# "Summarize the following text in <<style>> style: <<text>>"

result = send_from_library(
    library_path=LIBRARY,
    key="summarize",
    values={
        "text":  "Artificial intelligence is transforming every industry "
                 "from healthcare to finance.",
        "style": "bullet points"
    }
)
print(result)

# ---------------------------------------------------------------------------
# 7c. Library prompt with <<placeholders>> — stateful chat
# ---------------------------------------------------------------------------
print("\n=== 7c. Library prompt with placeholders (stateful chat) ===")

ai_ph = make_ai()
ai_ph.load_library(LIBRARY)

print(ai_ph.send_chat_prompt_from_library(
    key="summarize",
    values={
        "text":  "Orcas are apex predators that hunt in coordinated packs.",
        "style": "one sentence"
    }
))
# Memory is active — follow-up needs no library
print(ai_ph.send_chat_prompt("Now expand that into three bullet points."))


# ---------------------------------------------------------------------------
# 8. Prompt library — stateful chat with memory
# ---------------------------------------------------------------------------
print("\n=== 8. Library prompt (stateful chat) ===")
ai_lib = make_ai()
ai_lib.load_library(LIBRARY)
print(ai_lib.send_chat_prompt_from_library(
    key="summarize",
    values={"text": "Orcas are large dolphins, black and white, and hunt in packs. They are top of the food chain!"}
))
print(ai_lib.send_chat_prompt("Can you make that shorter?"))   # memory active

# ---------------------------------------------------------------------------
# 9. Inspect — model listing and token counting
# ---------------------------------------------------------------------------
print("\n=== 9. Inspect: model list ===")
models = list_models()   # uses defaults
for m in models[:5]:
    print(f"  {m}")

print("\n=== 9. Inspect: token count ===")
sample = "The quick brown fox jumps over the lazy dog."
print(f"  '{sample}' → {count_tokens(sample)} tokens")

# ---------------------------------------------------------------------------
# 10. Inspect — prompt preview (no API call)
# ---------------------------------------------------------------------------
print("\n=== 10. Inspect: prompt preview ===")
library_obj = inspect.load_library(LIBRARY)
prompts = inspect.list_prompts(library_obj)
print(f"  Available prompts: {prompts}")
print(f"  Preview 'summarize': {inspect.preview_prompt(library_obj, 'summarize')}")

# ---------------------------------------------------------------------------
# 11. Inspect — account info (Venice only)
# ---------------------------------------------------------------------------
if PROVIDER == "Venice":
    print("\n=== 11. Inspect: account info ===")
    info = inspect.account_info(api_key=API_KEY)
    # Print each section separately
    print(f"  API Keys:          {info.get('api_keys', {})}")
    print(f"  Key Rate Limits:   {info.get('key_rate_limits', {})}")
    print(f"  Model Rate Limits: {info.get('model_rate_limits', {})}")
else:
    print("\n=== 11. Inspect: account info (skipped — Venice only) ===")



