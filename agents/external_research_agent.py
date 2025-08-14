# agents/external_research_agent.py
import requests
import json
from openai import OpenAI
from utils.chunking import chunk_text
from config import settings

class ExternalResearchAgent:
    """
    Stage 1 Automated External Research Agent
    Uses OpenAI GPT model with web_search_preview tool, authenticated via internal token service.
    Gathers current, reputable, and relevant external intel for a given topic & business function.
    """

    def __init__(self, topic: str, business_function: str):
        self.topic = topic
        self.business_function = business_function
        self.client = self._get_openai_client()

    def _get_openai_client(self) -> OpenAI:
        """
        Retrieve an OpenAI API key from the internal token service and return a configured client.
        """
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
            raise RuntimeError("No 'openai_api_key' in token service response.")

        return OpenAI(api_key=api_key, timeout=60)

    def run(self) -> str:
        """
        Perform the automated external research via web search.
        """
        input_text = (
            f"You are an expert researcher. Perform live web research to provide the most recent, "
            f"credible, and relevant information on the topic '{self.topic}' in context of the "
            f"business function '{self.business_function}'. Include trends, statistics, competitors, "
            f"risks, opportunities, and emerging technologies. Use markdown headings for sections."
        )

        print(f"[ExternalResearchAgent] Running web search + GPT for '{self.topic}' / '{self.business_function}'...")
        try:
            response = self.client.responses.create(
                model=settings.OPENAI_MODEL,
                input=input_text,
                tools=[{"type": "web_search_preview"}]
            )

            raw_output = response.output_text or ""
            chunks = chunk_text(raw_output)
            print(f"[ExternalResearchAgent] Research complete — {len(chunks)} chunk(s) produced.")
            return "\n".join(chunks)

        except Exception as e:
            print(f"[ExternalResearchAgent] ERROR: {e}")
            return f"(Error during external research: {e})"