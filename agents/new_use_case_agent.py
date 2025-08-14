# agents/new_use_case_agent.py
import os
import json
from typing import List, Dict
from utils.chunking import chunk_text
from utils.schema_definitions import NewUseCaseRecord, new_use_case_columns
from config import settings
import pandas as pd
import requests
from openai import OpenAI

class NewUseCaseAgent:
    """
    Stage 3 New Use Case Generation Agent
    Generates use cases in batches of 5 per pass until targets are met, with checkpoint/resume capability.
    """

    def __init__(self, target_core=30, target_noncore=10, batch_size=5, checkpoint_file="stage3_checkpoint.json"):
        self.target_core = target_core
        self.target_noncore = target_noncore
        self.batch_size = batch_size
        self.checkpoint_path = os.path.join(settings.OUTPUT_DIR, checkpoint_file)
        self.client = self._get_openai_client()
        self.existing_records: List[Dict] = self._load_checkpoint()

    def _get_openai_client(self) -> OpenAI:
        """Fetch API key from token service and return OpenAI client."""
        payload = {
            "workspace_id": settings.WORKSPACE_ID,
            "model_name": settings.OPENAI_MODEL,
            "oai_access": "openai_direct"
        }
        resp = requests.post(settings.TOKEN_SERVICE_URL, json=payload)
        resp.raise_for_status()
        credentials = json.loads(resp.content)
        api_key = credentials.get("openai_api_key")
        if not api_key:
            raise RuntimeError("No 'openai_api_key' in token service response.")
        return OpenAI(api_key=api_key, timeout=90)

    def _load_checkpoint(self) -> List[Dict]:
        """Load previously saved use case records if checkpoint exists."""
        if os.path.exists(self.checkpoint_path):
            try:
                with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                print(f"[NewUseCaseAgent] Loaded checkpoint with {len(data)} existing records.")
                return data
            except Exception as e:
                print(f"[NewUseCaseAgent] Failed to load checkpoint: {e}")
        return []

    def _save_checkpoint(self):
        """Save current records to checkpoint file."""
        try:
            with open(self.checkpoint_path, "w", encoding="utf-8") as f:
                json.dump(self.existing_records, f, ensure_ascii=False, indent=2)
            print(f"[NewUseCaseAgent] Checkpoint saved with {len(self.existing_records)} records.")
        except Exception as e:
            print(f"[NewUseCaseAgent] ERROR saving checkpoint: {e}")

    def run(self) -> str:
        """
        Multi-pass generation until targets reached.
        Returns:
            str: Path to final XLSX file containing all generated use cases.
        """
        print("[NewUseCaseAgent] Starting multi-pass use case generation...")

        core_count = len([r for r in self.existing_records if r.get("type") == "core"])
        noncore_count = len([r for r in self.existing_records if r.get("type") == "non-core"])

        while core_count < self.target_core or noncore_count < self.target_noncore:
            needed_core = self.target_core - core_count
            needed_noncore = self.target_noncore - noncore_count

            batch_core = min(self.batch_size, needed_core)
            batch_noncore = min(self.batch_size, needed_noncore)

            if batch_core == 0 and batch_noncore == 0:
                break

            prompt = (
                f"Generate {batch_core} CORE and {batch_noncore} NON-CORE AI/automation business use cases.\n"
                "Each record must strictly follow this format:\n"
                "Title, Description, Category, Estimated Impact, Complexity, Confidence, Strategic Fit, Type.\n"
                "Type must be 'core' or 'non-core' as requested.\n"
                "Ensure titles are unique. Be concise but clear.\n"
            )

            try:
                resp = self.client.responses.create(
                    model=settings.OPENAI_MODEL,
                    input=prompt
                )
                generated_text = resp.output_text or ""
                chunks = chunk_text(generated_text, chunk_size=3000)  # safe split if needed
                for chunk in chunks:
                    rows = [row.strip() for row in chunk.split("\n") if row.strip()]
                    for row in rows:
                        try:
                            parts = [p.strip() for p in row.split(",")]
                            if len(parts) >= 8:
                                record = NewUseCaseRecord(
                                    title=parts[0],
                                    description=parts[1],
                                    category=parts[2],
                                    impact=parts[3],
                                    complexity=parts[4],
                                    confidence=parts[5],
                                    strategic_fit=parts[6],
                                    type=parts[7].lower()
                                )
                                self.existing_records.append(record.dict())
                        except Exception as e:
                            print(f"[NewUseCaseAgent] Skipping malformed row: {e}")

                # Save checkpoint after each batch
                self._save_checkpoint()

                # Update counts
                core_count = len([r for r in self.existing_records if r.get("type") == "core"])
                noncore_count = len([r for r in self.existing_records if r.get("type") == "non-core"])

            except Exception as e:
                print(f"[NewUseCaseAgent] ERROR during batch generation: {e}")
                break

        # Export final XLSX
        output_path = os.path.join(settings.OUTPUT_DIR, "stage3_new_use_cases.xlsx")
        try:
            df = pd.DataFrame(self.existing_records, columns=new_use_case_columns)
            df.to_excel(output_path, index=False)
            print(f"[NewUseCaseAgent] Final XLSX saved to {output_path}")
            return output_path
        except Exception as e:
            print(f"[NewUseCaseAgent] ERROR exporting XLSX: {e}")
            return f"(Error exporting XLSX: {e})"