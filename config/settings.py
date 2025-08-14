# config/settings.py
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# ==== API KEYS & ENDPOINTS ====
# OpenAI / internal token service
WORKSPACE_ID = os.getenv("WORKSPACE_ID", "WORKSPACE_ID_PLACEHOLDER")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
TOKEN_SERVICE_URL = os.getenv(
    "TOKEN_SERVICE_URL",
    "https://aiplatform.gcs.int.thomsonreuters.com/v1/openai/token"
)

# Anthropic keys if needed later
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# AWS placeholders (future S3/Dynamo/EventBridge use)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# ==== BUDGET CAPS (USD) from requirements doc ====
BUDGET_CAPS = {
    "stage0_L2": 15,
    "stage1": 25,
    "stage2": 60,
    "stage3": 200,
    "stage4": 80
}

# ==== OUTPUT + TEMP DIRECTORIES ====
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==== CHUNKING/TOKEN SAFETY SETTINGS ====
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "8000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# ==== PROMPT COMPATIBILITY MATRIX ====
PROMPT_MATRIX_PATH = os.path.join(BASE_DIR, "config", "prompt_compatibility_matrix.json")