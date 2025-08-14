# agents/dedup_agent.py
from typing import List, Dict
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import settings

class DedupAgent:
    """
    Deduplication Agent for Stage 3:
    Removes near-duplicate use cases based on title similarity and combined field similarity.
    """

    def __init__(self, records: List[Dict], title_threshold: float = 0.88, combined_threshold: float = 0.85):
        self.records = records or []
        self.title_threshold = title_threshold
        self.combined_threshold = combined_threshold

    def _vectorize_and_compare(self, texts: List[str]) -> np.ndarray:
        """Vectorizes text and returns cosine similarity matrix."""
        if not texts:
            return np.array([])
        vectorizer = TfidfVectorizer().fit_transform(texts)
        return cosine_similarity(vectorizer)

    def run(self) -> List[Dict]:
        if not self.records:
            print("[DedupAgent] No records provided for deduplication.")
            return []

        df = pd.DataFrame(self.records)
        keep_mask = np.ones(len(df), dtype=bool)

        # Title-based similarity
        title_sims = self._vectorize_and_compare(df["title"].astype(str).tolist())
        # Combined field similarity
        combined_text = (df["title"].astype(str) + " " + df["description"].astype(str)).tolist()
        combined_sims = self._vectorize_and_compare(combined_text)

        for i in range(len(df)):
            if not keep_mask[i]:
                continue
            for j in range(i + 1, len(df)):
                if not keep_mask[j]:
                    continue
                if (
                    title_sims[i, j] >= self.title_threshold
                    or combined_sims[i, j] >= self.combined_threshold
                ):
                    print(f"[DedupAgent] Removing duplicate: '{df.loc[j, 'title']}' ~ '{df.loc[i, 'title']}'")
                    keep_mask[j] = False

        deduped_df = df[keep_mask].reset_index(drop=True)
        print(f"[DedupAgent] Reduced from {len(df)} to {len(deduped_df)} records after deduplication.")
        return deduped_df.to_dict(orient="records")