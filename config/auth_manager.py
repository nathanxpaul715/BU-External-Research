import json  
import os  
import time  
import requests  
from typing import Optional  
from config.settings import WORKSPACE_ID, TOKEN_URL, TOKEN_CACHE_FILE, TOKEN_EXPIRY_SECONDS

  
class TokenManager:  
    """Manages dynamic API token fetching and caching"""
      
    def __init__(self):  
        self.token_cache_file = TOKEN_CACHE_FILE  
        self.token_expiry_seconds = TOKEN_EXPIRY_SECONDS
      
    def _fetch_new_token(self) -> dict:  
        """Fetch a fresh token from the TR endpoint"""  
        payload = {"workspace_id": WORKSPACE_ID}
          
        try:  
            resp = requests.post(TOKEN_URL, headers=None, json=payload)  
            resp.raise_for_status()  
            credentials = resp.json()
              
            if 'anthropic_api_key' not in credentials:  
                raise ValueError(f"API key not found in response: {credentials}")
              
            # Add timestamp for cache management  
            credentials['fetched_at'] = time.time()  
            return credentials
              
        except requests.RequestException as e:  
            raise Exception(f"Failed to fetch token: {e}")
      
    def _save_token_cache(self, credentials: dict):  
        """Save token to local cache file"""  
        with open(self.token_cache_file, 'w') as f:  
            json.dump(credentials, f)
      
    def _load_token_cache(self) -> Optional[dict]:  
        """Load token from cache if exists and not expired"""  
        if not os.path.exists(self.token_cache_file):  
            return None
          
        try:  
            with open(self.token_cache_file, 'r') as f:  
                credentials = json.load(f)
              
            # Check if token is expired  
            fetched_at = credentials.get('fetched_at', 0)  
            if time.time() - fetched_at > self.token_expiry_seconds:  
                return None  # Token expired
              
            return credentials
              
        except (json.JSONDecodeError, OSError):  
            return None
      
    def get_api_key(self, force_refresh: bool = False) -> str:  
        """  
        Get valid API key (from cache or fetch new)
          
        Args:  
            force_refresh: Force fetching a new token
          
        Returns:  
            Valid Anthropic API key  
        """  
        if not force_refresh:  
            cached = self._load_token_cache()  
            if cached and 'anthropic_api_key' in cached:  
                return cached['anthropic_api_key']
          
        # Fetch new token  
        credentials = self._fetch_new_token()  
        self._save_token_cache(credentials)  
        return credentials['anthropic_api_key']

  
# Singleton instance  
_token_manager = TokenManager()
  
def get_api_key(force_refresh: bool = False) -> str:  
    """Convenience function to get API key"""  
    return _token_manager.get_api_key(force_refresh)