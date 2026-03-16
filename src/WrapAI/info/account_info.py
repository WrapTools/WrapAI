# info/account_info.py

import requests
import logging

# Logger Configuration
logger = logging.getLogger(__name__)

from ..core.wv_core import KEY_URL, RATE_LIMIT_API_URL, RATE_LIMIT_MODEL_URL

class VeniceApiKeyInfo:
    def __init__(self, api_key):
        self.api_key = api_key

    def list_api_keys(self):
        url = KEY_URL

        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors

        return response

    def list_api_key_rate_limits(self):
        url = RATE_LIMIT_API_URL

        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors

        return response

    def get_model_rate_limits(self):
        url = RATE_LIMIT_MODEL_URL

        headers = {f"Authorization": f"Bearer {self.api_key}"}
        response = requests.request("GET", url, headers=headers)

        return response
