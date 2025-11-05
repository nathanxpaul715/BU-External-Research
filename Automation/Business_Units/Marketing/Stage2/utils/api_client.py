"""Centralized API Client for Thomson Reuters Anthropic Token Management
This utility manages API tokens with automatic refresh to avoid rate limits
"""
import anthropic
import requests
import json
import time
from typing import Optional
from threading import Lock


class AnthropicAPIClient:
    """
    Centralized Anthropic API client that uses TR's token endpoint
    to get fresh API keys with higher rate limits
    """

    def __init__(self, workspace_id: str, token_url: str):
        """
        Initialize the API client

        Args:
            workspace_id: Thomson Reuters workspace ID
            token_url: TR token endpoint URL
        """
        self.workspace_id = workspace_id
        self.token_url = token_url
        self.client: Optional[anthropic.Anthropic] = None
        self.api_key: Optional[str] = None
        self.last_refresh_time: float = 0
        self.refresh_interval: int = 300  # Refresh every 5 minutes
        self.lock = Lock()

        # Initialize on creation
        self._refresh_token()

    def _refresh_token(self) -> bool:
        """
        Fetch a new API token from TR endpoint

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            payload = {"workspace_id": self.workspace_id}
            resp = requests.post(self.token_url, headers=None, json=payload)
            credentials = json.loads(resp.content)

            if 'anthropic_api_key' in credentials:
                self.api_key = credentials["anthropic_api_key"]
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.last_refresh_time = time.time()
                return True
            else:
                print(f"Failed to get API key from TR endpoint: {credentials}")
                return False

        except Exception as e:
            print(f"Error refreshing token: {e}")
            return False

    def _ensure_fresh_token(self):
        """
        Ensure we have a fresh token, refresh if needed
        """
        with self.lock:
            current_time = time.time()
            time_since_refresh = current_time - self.last_refresh_time

            # Refresh if it's been more than refresh_interval
            if time_since_refresh >= self.refresh_interval:
                print(f"Token refresh triggered (last refresh: {int(time_since_refresh)}s ago)")
                self._refresh_token()

    def get_client(self) -> anthropic.Anthropic:
        """
        Get the Anthropic client with a fresh token

        Returns:
            anthropic.Anthropic: Configured Anthropic client
        """
        self._ensure_fresh_token()
        return self.client

    def create_message(self, **kwargs):
        """
        Create a message with automatic token refresh and retry logic

        This wraps the Anthropic messages.create() call with:
        - Automatic token refresh
        - Retry logic for rate limit errors with long waits

        Args:
            **kwargs: Arguments to pass to client.messages.create()

        Returns:
            Message response from Anthropic API
        """
        max_retries = 3
        retry_delay = 60  # Start with 60 seconds to wait for rate limit window to pass

        for attempt in range(max_retries):
            try:
                self._ensure_fresh_token()
                client = self.get_client()
                return client.messages.create(**kwargs)

            except anthropic.RateLimitError as e:
                if attempt < max_retries - 1:
                    print(f"[RATE LIMIT] Hit workspace limit of 100k tokens/min")
                    print(f"[RATE LIMIT] Waiting {retry_delay}s for rate limit window to reset... (attempt {attempt + 1}/{max_retries})")
                    # Force token refresh
                    with self.lock:
                        self._refresh_token()
                    time.sleep(retry_delay)
                    retry_delay = 60  # Keep at 60s since we need to wait for the 1-minute window
                else:
                    print(f"[ERROR] Rate limit error after {max_retries} attempts")
                    print(f"[ERROR] The workspace rate limit is 100,000 tokens per minute")
                    print(f"[ERROR] Consider reducing max_tokens or adding delays between requests")
                    raise

            except Exception as e:
                print(f"[ERROR] API error: {e}")
                raise

        raise Exception("Failed to create message after all retries")


# Global client instance (singleton pattern)
_global_client: Optional[AnthropicAPIClient] = None


def get_api_client(workspace_id: str, token_url: str) -> AnthropicAPIClient:
    """
    Get or create the global API client instance

    Args:
        workspace_id: Thomson Reuters workspace ID
        token_url: TR token endpoint URL

    Returns:
        AnthropicAPIClient: Configured API client
    """
    global _global_client

    if _global_client is None:
        _global_client = AnthropicAPIClient(workspace_id, token_url)
        print("[OK] Anthropic API client initialized with TR token endpoint")

    return _global_client
