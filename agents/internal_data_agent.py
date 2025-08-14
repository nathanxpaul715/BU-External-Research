# agents/internal_data_agent.py
import os
from utils.normalization import normalize_any

class InternalDataAgent:
    """
    Stage 2 Internal Data Agent
    Accepts a DOCX or PDF file (uploaded locally for MVP) and normalizes it into plain text.
    """

    def __init__(self, file_path: str):
        """
        Args:
            file_path (str): Path to the internal document file
        """
        self.file_path = file_path

    def run(self) -> str:
        """
        Execute normalization process.
        Returns:
            str: Cleaned, plain text extracted from input file.
        """
        if not self.file_path or not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"[InternalDataAgent] File not provided or does not exist: {self.file_path}"
            )

        try:
            print(f"[InternalDataAgent] Normalizing internal file: {self.file_path}")
            text_output = normalize_any(self.file_path)
            print(f"[InternalDataAgent] Normalization complete. Extracted {len(text_output)} characters.")
            return text_output
        except Exception as e:
            print(f"[InternalDataAgent] ERROR: Normalization failed for {self.file_path} — {e}")
            return f"(Error during internal data normalization: {e})"