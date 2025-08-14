# agents/gap_analysis_agent.py
from utils.chunking import chunk_text
from config import settings
from openai import OpenAI
import requests
import json

class GapAnalysisAgent:
    """
    Stage 1 Gap Analysis Agent
    Compares manual intelligence with automated external research and identifies missing pieces,
    inconsistencies, or opportunities for enrichment.
    """

    def __init__(self, manual_input: str, automated_input: str):
        self.manual_input = manual_input or ""
        self.automated_input = automated_input or ""
        self.client = self._get_openai_client()

    def _get_openai_client(self) -> OpenAI:
        """Fetch API key from internal token service and return OpenAI client."""
        payload = {
            "workspace_id": settings.WORKSPACE_ID,
            "model_name": settings.OPENAI_MODEL,
            "oai_access": "openai_direct"
        }
        resp = requests.post(settings.TOKEN_SERVICE_URL, json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"Token service error {resp.status_code}: {resp.text}")

        credentials = json.loads(resp.content)
        api_key = credentials.get("openai_api_key")
        if not api_key:
            raise RuntimeError("No 'openai_api_key' found in token service response.")

        return OpenAI(api_key=api_key, timeout=60)

    def run(self) -> str:
        """Perform gap analysis between manual and automated inputs."""
        if not self.automated_input and not self.manual_input:
            return "(No input provided for gap analysis.)"

        prompt = (
            "You are a senior analyst assigned to identify intelligence gaps.\n\n"
            "=== Manual Intelligence ===\n"
            f"{self.manual_input}\n\n"
            "=== Automated Research Intelligence ===\n"
            f"{self.automated_input}\n\n"
            "Instructions:\n"
            "1. Compare both sources.\n"
            "2. List missing key facts, themes, or data points from the automated research.\n"
            "3. Note contradictions or inconsistencies.\n"
            "4. Suggest what should be researched further to fill the gaps.\n"
            "Present results in markdown with headings: 'Missing Intel', 'Contradictions', 'Recommended Next Research'."
        )

        try:
            print("[GapAnalysisAgent] Running gap analysis between manual and automated sources...")
            response = self.client.responses.create(
                model=settings.OPENAI_MODEL,
                input=prompt
            )
            output_text = response.output_text or ""
            chunks = chunk_text(output_text)
            print(f"[GapAnalysisAgent] Gap analysis complete — {len(chunks)} chunk(s) produced.")
            return "\n".join(chunks)
        except Exception as e:
            print(f"[GapAnalysisAgent] ERROR: {e}")
            return f"(Error during gap analysis: {e})"