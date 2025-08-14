# agents/enrichment_agent.py
import os
import pandas as pd
from config import settings
from utils.schema_definitions import EnrichmentRecord, enrichment_columns

class EnrichmentAgent:
    """
    Stage 2 Enrichment Agent
    Transforms normalized internal data into a structured XLSX file
    with enrichment fields populated according to the business schema.
    """

    def __init__(self, internal_text: str, output_basename: str = "stage2_enrichment"):
        self.internal_text = internal_text or ""
        self.output_basename = output_basename

    def run(self) -> str:
        """
        Process normalized text into enrichment records and export as XLSX.
        Returns:
            str: Path of the generated XLSX file.
        """
        if not self.internal_text.strip():
            raise ValueError("No internal text provided to EnrichmentAgent.")

        print("[EnrichmentAgent] Starting enrichment process...")
        output_path = os.path.join(settings.OUTPUT_DIR, f"{self.output_basename}.xlsx")

        try:
            # For MVP: create mocked enrichment rows from internal text paragraphs
            paragraphs = [p.strip() for p in self.internal_text.split("\n") if p.strip()]
            records = []
            for para in paragraphs:
                # In a real system, this would be created via LLM mapping to schema
                record = EnrichmentRecord(
                    use_case_title=para[:60] + ("..." if len(para) > 60 else ""),
                    description=para,
                    source="Internal Document",
                    category="General",
                    tags="",
                    owner="",
                    last_updated="",
                    status=""
                )
                records.append(record.dict())

            # Make DataFrame with strict column order
            df = pd.DataFrame(records, columns=enrichment_columns)
            df.to_excel(output_path, index=False)
            print(f"[EnrichmentAgent] Enrichment XLSX saved to {output_path}")
            return output_path

        except Exception as e:
            print(f"[EnrichmentAgent] ERROR: {e}")
            return f"(Error during enrichment generation: {e})"