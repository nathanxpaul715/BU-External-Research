# config_tr_auth.py  
import json  
import os  
import time  
import requests  
from anthropic import Anthropic  
from dotenv import load_dotenv
  
load_dotenv()
  
WORKSPACE_ID = os.getenv("WORKSPACE_ID")  
TOKEN_URL = os.getenv("TOKEN_URL")  
TOKEN_CACHE_FILE = os.getenv("TOKEN_CACHE_FILE", ".api_token")  
TOKEN_EXPIRY_SECONDS = int(os.getenv("TOKEN_EXPIRY_SECONDS", "3600"))  
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
  
class TokenManager:  
    """Manages dynamic API token fetching and caching for Thomson Reuters"""
      
    def __init__(self):  
        self.token_cache_file = TOKEN_CACHE_FILE  
        self.token_expiry_seconds = TOKEN_EXPIRY_SECONDS
      
    def _fetch_new_token(self):  
        """Fetch a fresh token from the TR endpoint"""  
        payload = {"workspace_id": WORKSPACE_ID}
          
        try:  
            print(f"🔐 Fetching new token from TR endpoint...")  
            resp = requests.post(TOKEN_URL, headers=None, json=payload, timeout=30)  
            resp.raise_for_status()  
            credentials = resp.json()
              
            if 'anthropic_api_key' not in credentials:  
                raise ValueError(f"API key not found in response: {credentials}")
              
            # Add timestamp for cache management  
            credentials['fetched_at'] = time.time()  
            print(f"✅ Token fetched successfully")  
            return credentials
              
        except requests.RequestException as e:  
            print(f"❌ Failed to fetch token: {e}")  
            raise Exception(f"Failed to fetch token: {e}")
      
    def _save_token_cache(self, credentials):  
        """Save token to local cache file"""  
        try:  
            with open(self.token_cache_file, 'w') as f:  
                json.dump(credentials, f)  
            print(f"💾 Token cached to {self.token_cache_file}")  
        except OSError as e:  
            print(f"⚠️  Failed to cache token: {e}")
      
    def _load_token_cache(self):  
        """Load token from cache if exists and not expired"""  
        if not os.path.exists(self.token_cache_file):  
            print(f"📝 No token cache found")  
            return None
          
        try:  
            with open(self.token_cache_file, 'r') as f:  
                credentials = json.load(f)
              
            # Check if token is expired  
            fetched_at = credentials.get('fetched_at', 0)  
            age = time.time() - fetched_at
              
            if age > self.token_expiry_seconds:  
                print(f"⏰ Token expired (age: {age:.0f}s > {self.token_expiry_seconds}s)")  
                return None  # Token expired
              
            print(f"✅ Using cached token (age: {age:.0f}s)")  
            return credentials
              
        except (json.JSONDecodeError, OSError) as e:  
            print(f"⚠️  Failed to load token cache: {e}")  
            return None
      
    def get_api_key(self, force_refresh=False):  
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
  
def get_anthropic_client(force_refresh=False):  
    """  
    Get configured Anthropic client with TR authentication
      
    Args:  
        force_refresh: Force fetching a new token
      
    Returns:  
        Configured Anthropic client  
    """  
    api_key = _token_manager.get_api_key(force_refresh)  
    return Anthropic(api_key=api_key)