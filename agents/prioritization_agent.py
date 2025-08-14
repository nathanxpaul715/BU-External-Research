# agents/prioritization_agent.py
from typing import List, Dict
import pandas as pd

class PrioritizationAgent:
    """
    Stage 3 Prioritization Agent
    Applies priority scoring to validated use cases and sorts by score descending.
    """

    # Map qualitative labels to numeric scores for calculation
    SCORE_MAP = {
        "H": 3,
        "M": 2,
        "L": 1
    }

    def __init__(self, records: List[Dict]):
        self.records = records or []

    def _score_field(self, val):
        """
        Convert a field value (string/number) to a numeric score.
        Accepts numeric string, int, float, or H/M/L.
        """
        if val is None:
            return 0
        if isinstance(val, (int, float)):
            return float(val)
        val_str = str(val).strip()
        if val_str.upper() in self.SCORE_MAP:
            return self.SCORE_MAP[val_str.upper()]
        try:
            return float(val_str)
        except ValueError:
            return 0

    def run(self) -> List[Dict]:
        if not self.records:
            print("[PrioritizationAgent] No records provided for prioritization.")
            return []

        print(f"[PrioritizationAgent] Calculating priority scores for {len(self.records)} records...")
        df = pd.DataFrame(self.records)

        df["impact_score"] = df["impact"].apply(self._score_field)
        df["complexity_score"] = df["complexity"].apply(self._score_field)
        df["confidence_score"] = df["confidence"].apply(self._score_field)
        df["strategic_score"] = df["strategic_fit"].apply(self._score_field)

        # Weighted formula from requirements doc
        df["priority_score"] = (
            0.4 * df["impact_score"] +
            0.3 * df["complexity_score"] +
            0.2 * df["confidence_score"] +
            0.1 * df["strategic_score"]
        )

        # Sort by score descending
        df = df.sort_values(by="priority_score", ascending=False).reset_index(drop=True)

        print("[PrioritizationAgent] Prioritization complete. Top 5 titles:")
        print(df["title"].head().tolist())

        # Drop intermediate scoring columns before returning
        return df.drop(columns=["impact_score", "complexity_score", "confidence_score", "strategic_score"]).to_dict(orient="records")