# prompt/prompt_text.py

import logging

logger = logging.getLogger(__name__)

CHAT_COMPLETION = "/chat/completions"

import json
import hashlib
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from collections.abc import Iterator

from WrapEmit import status, error

from ..core.prompt_attributes import OpenAIPromptAttributes, VenicePromptAttributes, VeniceParameters
from ..core.prompt_response import PromptResponse
from ..core.wv_core import BASE_VENICE_URL, BASE_OPENAI_URL
from ..utils.markdown import MarkdownToText
from ..utils.secret_loader import load_secret
from ..core.wv_core import PROVIDER_OPENAI, PROVIDER_VENICE
from ..core.provider_config import ProviderConfig

TIMEOUT=1800

def get_prompt_runner(api_key_type: str, model: str, base_url=None, provider=PROVIDER_VENICE):
    """
        Returns a configured prompt runner (Venice or OpenAI) based on the provider.

        Args:
            api_key_type: Key used with load_secret to fetch API key.
            model: Model name (e.g., "gpt-4", "qwen-2.5").
            base_url: Optional override for API base URL.
            provider: "venice" (default) or "openai".

        Returns:
            Instance of VeniceTextPrompt or OpenAITextPrompt.
    """

    api_key = load_secret(api_key_type)
    if provider == PROVIDER_VENICE:
        return VeniceTextPrompt(api_key=api_key, model=model, base_url=base_url)
    elif provider == PROVIDER_OPENAI:
        return OpenAITextPrompt(api_key=api_key, model=model, base_url=base_url)
    else:
        raise ValueError(f"Unknown provider: {provider}")



# class OpenAITextPrompt:
#     def __init__(self, api_key: str, model: str, base_url: str = BASE_OPENAI_URL):
#         self.api_key = api_key
#         self.model = model
#         self.base_url = base_url
class OpenAITextPrompt:
    def __init__(self, api_key_or_config: ProviderConfig = None, **kwargs):
        if isinstance(api_key_or_config, ProviderConfig):
            config = api_key_or_config
            self.api_key = config.api_key
            self.model = config.get_model()
            self.base_url = config.base_url or BASE_OPENAI_URL
        else:
            # Legacy style: all values must be in kwargs
            self.api_key = kwargs.get("api_key")
            self.model = kwargs.get("model")
            self.base_url = kwargs.get("base_url", BASE_OPENAI_URL)

            if not self.api_key or not self.model:
                raise ValueError("Must provide either a ProviderConfig or api_key + model.")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.attributes = OpenAIPromptAttributes()
        self.parsed_response: Optional[PromptResponse] = None
        self.last_user_prompt: str = ""
        self.last_system_prompt: str = ""

    def set_attributes(self, **kwargs):
        """Dynamically assign attributes."""
        for key, value in kwargs.items():
            if hasattr(self.attributes, key):
                setattr(self.attributes, key, value)
            else:
                logger.warning(f"Unknown attribute '{key}' ignored.")

    def prompt(self, user_prompt: str, system_prompt: str = "You are a helpful assistant.", messages=None) -> Optional[PromptResponse]:
        self.last_user_prompt = user_prompt
        self.last_system_prompt = system_prompt

        if messages is None:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

        payload = {
            "model": self.model,
            "messages": messages,
            **self.attributes.to_dict(skip_none=True)
        }

        logger.info("OpenAI Payload running")
        logger.debug(f"OpenAI Payload\n{payload}")

        status("Sending request to OpenAI…")

        try:
            response = requests.post(
                f"{self.base_url}{CHAT_COMPLETION}",
                headers=self.headers,
                json=payload,
                # timeout=300
                timeout=TIMEOUT
            )
            logger.debug(f"API response status: {response.status_code}")
            logger.debug(f"{response=}")
            data = response.json()

            if "error" in data:
                logger.error(f"API Error: {data['error']}")
                return None

            self.parsed_response = self.parse_response(data)
            return self.parsed_response

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None

    def parse_response(self, response_json: dict) -> PromptResponse:
        content = response_json.get('choices', [{}])[0].get('message', {}).get('content', '')
        think, response = "", ""

        if '</think>' in content:
            parts = content.split('</think>', 1)
            think = parts[0].replace('<think>', '').strip()
            response = parts[1].strip()
        else:
            response = content.strip()

        return PromptResponse(
            model=response_json.get('model'),
            created=response_json.get('created'),
            usage=response_json.get('usage', {}),
            think=think,
            response=response.replace('<think>', '').replace('</think>', ''),
            citations=[],  # OpenAI doesn't have citations
            parameters=self.attributes.to_dict(skip_none=True),
            system_prompt=self.last_system_prompt,
            user_prompt=self.last_user_prompt
        )

    # Accessors
    def get_response(self) -> str:
        return self.parsed_response.response if self.parsed_response else ""

    def get_think(self) -> str:
        return self.parsed_response.think if self.parsed_response else ""

    def get_model(self) -> str:
        return self.parsed_response.model if self.parsed_response else "N/A"

    def get_usage(self) -> Dict:
        return self.parsed_response.usage if self.parsed_response else {}

    # Saving
    def save_all(self, file_path: str | Path):
        if not self.parsed_response:
            logger.warning("No response to save.")
            return
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        self.parsed_response.to_json(file_path, app_name="OpenAIPrompt", data_version="1.0")

    def save_response(self, file_path: str | Path):
        response = self.get_response()
        if response:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(response, encoding="utf-8")

    def save_text_response(self, md_file_path: str | Path, output_path: str | Path):
        try:
            md_handler = MarkdownToText(md_file_path)
            md_handler.save_clean_text(output_path)
            logger.info(f"Saved clean text to {output_path}")
        except Exception as e:
            logger.error(f"Error saving clean text: {e}")

    # Hashing
    def get_structured_payload_for_hash(self, document_id: str, user_prompt: str, system_prompt: str, user_prompt_type="request") -> dict:
        return {
            "document_id": document_id,
            "system_prompt": system_prompt,
            user_prompt_type: {
                "model": self.model,
                "user_prompt": user_prompt,
                "parameters": self.attributes.to_dict(skip_none=True)
            }
        }

    def get_hash(self, structured_payload: dict) -> str:
        return hashlib.sha256(json.dumps(structured_payload, sort_keys=True).encode()).hexdigest()


    # -------------------------- NEW --------------------------------------
    def _iter_sse_data(self, response: requests.Response) -> Iterator[str]:
        """
        Iterate Server-Sent Events 'data:' payloads.
        Stops on [DONE].

        This is protocol-level logic and should remain private.
        """
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            if not line.startswith("data:"):
                continue

            data = line[len("data:"):].strip()
            if data == "[DONE]":
                return

            yield data

    def prompt_stream_events(
        self,
        user_prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        messages=None,
    ) -> Iterator[dict]:
        """
        FUTURE EXTENSION POINT

        Stream raw event dictionaries from the provider.

        Intended future uses:
            - Rich delta events (role changes, tool calls, etc.)
            - Streaming structured JSON
            - Provider-specific metadata
            - Citations
            - Usage blocks
            - Reasoning / thinking tokens

        Current implementation:
            Not implemented yet.
            Use prompt_stream() for text-only streaming.

        When implemented, this should:
            1. Make the streaming POST request (stream=True)
            2. Parse SSE lines
            3. json.loads() each chunk
            4. yield the full chunk dict
        """
        raise NotImplementedError(
            "prompt_stream_events() is reserved for future rich streaming support."
        )

    def prompt_stream(
            self,
            user_prompt: str,
            system_prompt: str = "You are a helpful assistant.",
            messages=None,
    ) -> Iterator[str]:
        """
        Stream text delta chunks only.

        This is the stable public streaming API.
        """
        self.last_user_prompt = user_prompt
        self.last_system_prompt = system_prompt

        if messages is None:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

        payload = {
            "model": self.model,
            "messages": messages,
            **self.attributes.to_dict(skip_none=True),
            "stream": True,
        }

        headers = dict(self.headers)
        headers["Accept"] = "text/event-stream"

        with requests.post(
                f"{self.base_url}{CHAT_COMPLETION}",
                headers=headers,
                json=payload,
                stream=True,
                timeout=TIMEOUT,
        ) as resp:

            if resp.status_code != 200:
                try:
                    detail = resp.json()
                except Exception:
                    detail = resp.text
                raise requests.exceptions.HTTPError(
                    f"HTTP {resp.status_code}: {detail}",
                    response=resp,
                )

            for data in self._iter_sse_data(resp):
                chunk = json.loads(data)

                choices = chunk.get("choices") or []
                if not choices:
                    continue

                delta = choices[0].get("delta") or {}
                text = delta.get("content")
                if text:
                    yield text

    def prompt_stream_collect(
            self,
            user_prompt: str,
            system_prompt: str = "You are a helpful assistant.",
            messages=None,
    ) -> str:
        """
        Convenience: stream -> accumulate -> return full text.
        Useful for CLI/API cases where you want streaming to avoid idle timeouts
        but still return a single final string.
        """
        return "".join(self.prompt_stream(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            messages=messages,
        ))

class VeniceTextPrompt(OpenAITextPrompt):
    # def __init__(self, api_key: str, model: str, base_url: str = BASE_VENICE_URL):
    #     super().__init__(api_key, model, base_url)
    #     # Replace the OpenAI attributes with Venice attributes
    def __init__(self, api_key_or_config: ProviderConfig = None, **kwargs):
        if isinstance(api_key_or_config, ProviderConfig):
            if not api_key_or_config.base_url:
                api_key_or_config.base_url = BASE_VENICE_URL
        else:
            kwargs.setdefault("base_url", BASE_VENICE_URL)
        super().__init__(api_key_or_config, **kwargs)
        self.attributes = VenicePromptAttributes()

    def set_attributes(self, **kwargs):
        """Dynamically assign attributes or nested VeniceParameters."""
        for key, value in kwargs.items():
            if hasattr(self.attributes, key):
                if key == "venice_parameters":
                    if isinstance(value, dict):
                        self.attributes.venice_parameters = VeniceParameters(**value)
                    elif isinstance(value, VeniceParameters):
                        self.attributes.venice_parameters = value
                else:
                    setattr(self.attributes, key, value)
            else:
                logger.warning(f"Unknown attribute '{key}' ignored.")

    def prompt(self, user_prompt: str, system_prompt: str = "You are a helpful assistant.", messages=None,
               response_format: Optional[Dict[str, Any]] = None) -> Optional[PromptResponse]:

        self.last_user_prompt = user_prompt
        self.last_system_prompt = system_prompt

        if messages is None:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

        # Create the base payload without venice_parameters
        payload = {
            "model": self.model,
            "messages": messages,
            **{
                k: v for k, v in self.attributes.to_dict(skip_none=True).items()
                if k != "venice_parameters"
            }
        }

        # Add venice_parameters if they exist
        venice_data = self.attributes.venice_parameters.to_dict(skip_none=True)
        if venice_data:
            payload["venice_parameters"] = venice_data

        # Add response_format at the top level if provided
        if response_format:
            payload["response_format"] = response_format

        logger.info("Venice Payload running")
        logger.debug(f"Venice Payload\n{payload}")

        status("Sending request to Venice.ai…")

        try:
            response = requests.post(
                f"{self.base_url}{CHAT_COMPLETION}",
                headers=self.headers,
                json=payload,
                # timeout=300
                timeout=TIMEOUT
            )

            logger.debug(f"API response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            logger.debug(f"Raw response text: {response.text}")

            # Enhanced error handling
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"API HTTP Error: {error_msg}")
                error(error_msg)
                # raise requests.exceptions.HTTPError(error_msg)
                raise requests.exceptions.HTTPError(error_msg, response=response)

            try:
                data = response.json()
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON response: {response.text}"
                logger.error(error_msg)
                error(error_msg)
                raise ValueError(error_msg)

            # Check for API-level errors in the response
            if "error" in data:
                error_details = data["error"]
                if isinstance(error_details, dict):
                    error_msg = f"API Error - Type: {error_details.get('type', 'unknown')}, Message: {error_details.get('message', 'no message')}, Code: {error_details.get('code', 'no code')}"
                else:
                    error_msg = f"API Error: {error_details}"
                logger.error(error_msg)
                error(error_msg)
                raise ValueError(error_msg)

            self.parsed_response = self.parse_response(data)
            return self.parsed_response

        except requests.exceptions.RequestException as e:
            error_msg = f"Network/Request Error: {str(e)}"
            logger.error(error_msg)
            error(error_msg)
            raise
        except Exception as e:
            error_msg = f"Unexpected error in Venice API call: {str(e)}"
            logger.error(error_msg)
            raise

    def parse_response(self, response_json: dict) -> PromptResponse:
        # Override to include Venice-specific fields like citations
        content = response_json.get('choices', [{}])[0].get('message', {}).get('content', '')
        think, response = "", ""

        if '</think>' in content:
            parts = content.split('</think>', 1)
            think = parts[0].replace('<think>', '').strip()
            response = parts[1].strip()
        else:
            response = content.strip()

        return PromptResponse(
            model=response_json.get('model'),
            created=response_json.get('created'),
            usage=response_json.get('usage', {}),
            think=think,
            response=response.replace('<think>', '').replace('</think>', ''),
            citations=response_json.get("venice_parameters", {}).get("web_search_citations", []),
            parameters=self.attributes.to_dict(skip_none=True),
            system_prompt=self.last_system_prompt,
            user_prompt=self.last_user_prompt
        )

    def save_all(self, file_path: str | Path):
        if not self.parsed_response:
            logger.warning("No response to save.")
            return
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        self.parsed_response.to_json(file_path, app_name="VenicePrompt", data_version="1.0")

    def prompt_stream(
        self,
        user_prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        messages=None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> Iterator[str]:

        self.last_user_prompt = user_prompt
        self.last_system_prompt = system_prompt

        if messages is None:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

        payload = {
            "model": self.model,
            "messages": messages,
            **{
                k: v for k, v in self.attributes.to_dict(skip_none=True).items()
                if k != "venice_parameters"
            },
            "stream": True,
        }

        venice_data = self.attributes.venice_parameters.to_dict(skip_none=True)
        if venice_data:
            payload["venice_parameters"] = venice_data

        if response_format:
            payload["response_format"] = response_format

        headers = dict(self.headers)
        headers["Accept"] = "text/event-stream"

        with requests.post(
            f"{self.base_url}{CHAT_COMPLETION}",
            headers=headers,
            json=payload,
            stream=True,
            timeout=TIMEOUT,
        ) as resp:

            if resp.status_code != 200:
                raise requests.exceptions.HTTPError(
                    f"HTTP {resp.status_code}: {resp.text}",
                    response=resp,
                )

            for data in self._iter_sse_data(resp):
                chunk = json.loads(data)
                choices = chunk.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                text = delta.get("content")
                if text:
                    yield text

    def prompt_stream_collect(
        self,
        user_prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        messages=None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Venice version: supports response_format.
        """
        return "".join(self.prompt_stream(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            messages=messages,
            response_format=response_format,
        ))
