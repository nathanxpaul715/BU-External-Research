import os  
from dotenv import load_dotenv
  
load_dotenv()

# Thomson Reuters Authentication Configuration
WORKSPACE_ID = os.getenv("WORKSPACE_ID")  
TOKEN_URL = os.getenv("TOKEN_URL")  
TOKEN_CACHE_FILE = os.getenv("TOKEN_CACHE_FILE", ".api_token")  
TOKEN_EXPIRY_SECONDS = int(os.getenv("TOKEN_EXPIRY_SECONDS", "3600"))

# Anthropic Model Configuration  
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")

# Application Configuration  
MAX_TOKENS = 8000  
TEMPERATURE = 0.1 
USE_CASES_PER_SUB_FUNCTION = 8  
BATCH_SIZE = 3