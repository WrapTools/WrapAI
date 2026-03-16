# CHANGELOG

This changelog records project development history.  
Entries marked **Public release** were published to GitHub.

## [0.5.0] - 2026-03-16
### Public release
- First public release on GitHub


### Internal changes
- Removed generated example artifacts
- Standardized repository layout

## [0.4.5] - 2026-03-16
- Final cleanup and packaging updates prior to first public release

## [0.4.4] - 2026-03-15
- Added helper modules: `ai_helper`, `inspect`, and `open_provider`
- Updated module headers to include directory names

## [0.4.3] - 2026-03-14
- added standard license
- minor changes

## [0.4.2] - 2026-02-11
### Added
* Streaming support for text completions using Server-Sent Events (SSE).
* `prompt_stream(...) -> Iterator[str]` on text prompt runners (`OpenAITextPrompt`, `VeniceTextPrompt`) for incremental text chunk streaming.
* `prompt_stream_collect(...) -> str` convenience method to stream internally while returning a full accumulated response (useful for long prompts to avoid idle timeouts).
* `PromptRuntimeManager.stream_prompt(...) -> Iterator[str]` to stream via the manager using stored prompt templates and attributes.
* `PromptRuntimeManager.stream_prompt_collect(...) -> str` convenience wrapper for manager-based collection.
* Stubbed `prompt_stream_events(...) -> Iterator[dict]` for future rich event streaming (structured deltas, citations, tool calls, reasoning, etc.).

### Notes

* Existing non-streaming APIs (`prompt()`, `run_prompt()`) remain unchanged.
* Streaming currently emits text delta chunks only.
* Rich streaming events are reserved for future extension without breaking the current API.


## [0.4.1] - 2026-02-24
- Added directory placeholder in prompt_template

## [0.3.2] - 2026-02-07
- Migrated project to uv-managed `.venv`
- Declared `requires-python = ">=3.13"` in `pyproject.toml`
- Synced dependencies via `uv sync`
- Verified PyCharm 2025 compatibility

## [0.3.1] - 2026-01-21
- updated http errors to include more data -> raise requests.exceptions.HTTPError(error_msg, response=response)
- added token counting examples with file token counters

## [0.3.0] - 2026-01-20
- implemented WrapEmit and various small changes.  Next changes will be under a branch.

## [0.2.9] - 2025-07-31
- Update prior to adding chunking

## [0.2.8] - 2025-07-24
- Update prior to adding chunking
### Changes
- fixed file placeholders after it broke from pipelines changes 

## [0.2.7] - 2025-07-24
### Changes
- Miscellaneous changes 

## [0.2.6] - 2025-06-11
### Added
- reorganized into directories including core and providers
### Changed
- Updated examples

## [0.2.5] - 2025-06-06
### Added
- Added get_prompt_runner function to prompt_text
- Added prompt_manager_base.py
- Added to models.py
  - ModelRegistry class
  - OpenAIModels class

### Changed
- Updated PromptTemplate placeholder names
- Updated PromptTemplate to add Replace placeholder methods

## [0.2.4] - 2025-05-27
### Changed
- Miscellaneous change for initial release including account_info changes to return values instead of print them

## [0.2.3] - 2025-05-20
### Changed
- Updated the README.md file for api_key instructions

## [0.2.2] - 2025-05-19
### Added
- added support for new venice_parameters in the prompt_attributes
  - strip_thinking_response
  - disable_thinking
  - enable_web_citations
- added placeholders for additional OpenAIPromptAttributes not yet fully implemented

## [0.2.1] - 2025-05-19
### Added
- example_account_info.py file to show examples of using account_info.py module
- added def get_full_model_detail_dict method to VeniceModels class

### Removed
- removed application specific methods to show VeniceModel info in specific format.  Those should be in programs.
    - get_model_detail_dict
    - get_model_detail


## [0.2.0] - 2025-05-16
- Initial versioned release with CHANGELOG
