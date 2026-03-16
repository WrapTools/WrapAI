# prompt_executor.py

# IN DEVElOPMENT

import logging
import traceback
from typing import Any, Dict

logger = logging.getLogger(__name__)


class PromptExecutor:
    def __init__(self):
        pass

    def run_prompt(self, prompt: str, provider_instance: Any, **kwargs) -> Dict[str, Any]:
        """
        Enhanced run_prompt with comprehensive error handling and output capture
        """
        result = {
            'success': False,
            'output': None,
            'error': None,
            'full_response': None,
            'provider_info': None,
            'execution_details': {}
        }

        try:
            # Log execution start
            logger.info(f"Starting prompt execution with provider: {type(provider_instance).__name__}")

            # Fill placeholders and set attributes
            filled_prompt = self._fill_placeholders(prompt, **kwargs)
            self._set_provider_attributes(provider_instance, kwargs)

            # Store execution details
            result['execution_details'] = {
                'original_prompt': prompt,
                'filled_prompt': filled_prompt,
                'provider_type': type(provider_instance).__name__,
                'parameters': kwargs
            }

            # Execute prompt with detailed error capture
            response = provider_instance.run(filled_prompt)

            # Capture full response details
            result.update({
                'success': True,
                'output': response,
                'full_response': self._extract_full_response(response),
                'provider_info': self._get_provider_info(provider_instance)
            })

            logger.info("Prompt execution completed successfully")

        except Exception as e:
            # Comprehensive error capture
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'traceback': traceback.format_exc(),
                'provider_state': self._get_provider_state(provider_instance)
            }

            result['error'] = error_details

            # Log detailed error information
            logger.error(f"Prompt execution failed: {error_details['error_type']}")
            logger.error(f"Error message: {error_details['error_message']}")
            logger.debug(f"Full traceback:\n{error_details['traceback']}")

            # Print to screen for immediate visibility
            self._print_error_details(result)

        return result

    def _fill_placeholders(self, prompt: str, **kwargs) -> str:
        """Fill placeholders in prompt with provided values"""
        try:
            return prompt.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing placeholder value: {e}")

    def _set_provider_attributes(self, provider_instance: Any, kwargs: Dict) -> None:
        """Set provider attributes like temperature, top_p"""
        for attr in ['temperature', 'top_p', 'max_tokens']:
            if attr in kwargs:
                setattr(provider_instance, attr, kwargs[attr])

    def _extract_full_response(self, response: Any) -> Dict:
        """Extract comprehensive response details"""
        if hasattr(response, '__dict__'):
            return response.__dict__
        elif hasattr(response, 'to_dict'):
            return response.to_dict()
        else:
            return {'raw_response': str(response)}

    def _get_provider_info(self, provider_instance: Any) -> Dict:
        """Get provider configuration and state"""
        info = {
            'provider_type': type(provider_instance).__name__,
            'attributes': {}
        }

        # Common provider attributes
        for attr in ['temperature', 'top_p', 'max_tokens', 'model', 'api_key']:
            if hasattr(provider_instance, attr):
                value = getattr(provider_instance, attr)
                # Mask sensitive information
                if 'key' in attr.lower() and value:
                    value = f"{value[:8]}..." if len(value) > 8 else "***"
                info['attributes'][attr] = value

        return info

    def _get_provider_state(self, provider_instance: Any) -> Dict:
        """Get provider state for error diagnosis"""
        state = {}
        try:
            # Capture relevant provider state
            for attr in dir(provider_instance):
                if not attr.startswith('_') and not callable(getattr(provider_instance, attr)):
                    value = getattr(provider_instance, attr)
                    if 'key' in attr.lower() and value:
                        value = "***masked***"
                    state[attr] = value
        except Exception:
            state['error'] = "Could not capture provider state"

        return state

    def _print_error_details(self, result: Dict) -> None:
        """Print comprehensive error details to screen"""
        print("\n" + "="*80)
        print("PROMPT EXECUTION FAILED")
        print("="*80)

        error = result['error']
        details = result['execution_details']

        print(f"Provider: {details.get('provider_type', 'Unknown')}")
        print(f"Error Type: {error['error_type']}")
        print(f"Error Message: {error['error_message']}")

        print(f"\nOriginal Prompt:\n{details.get('original_prompt', 'N/A')}")
        print(f"\nFilled Prompt:\n{details.get('filled_prompt', 'N/A')}")

        print(f"\nParameters: {details.get('parameters', {})}")

        if error.get('provider_state'):
            print(f"\nProvider State: {error['provider_state']}")

        print(f"\nFull Traceback:\n{error['traceback']}")
        print("="*80 + "\n")

# Usage example with enhanced error handling
def execute_prompt_with_details(prompt_file: str, provider_instance: Any, **kwargs):
    """Helper function to execute prompts with full error details"""
    executor = PromptExecutor()

    try:
        with open(prompt_file, 'r') as f:
            prompt = f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file '{prompt_file}' not found")
        return None

    result = executor.run_prompt(prompt, provider_instance, **kwargs)

    if not result['success']:
        print("Execution failed - see error details above")
        return None

    return result['output']
