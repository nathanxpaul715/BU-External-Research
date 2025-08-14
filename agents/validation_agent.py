# agents/validation_agent.py
from typing import List, Dict
import re
import requests
from utils.schema_definitions import NewUseCaseRecord

class ValidationAgent:
    """
    Stage 3 Validation Agent
    Validates use case records for schema compliance, link accessibility,
    citation counts, basic PII detection, and confidence scoring.
    """

    def __init__(self, records: List[Dict]):
        self.records = records or []
        self.errors: List[str] = []

    def _check_links(self, text: str) -> bool:
        """Check all URLs in the given text return HTTP 200."""
        urls = re.findall(r'https?://\S+', text)
        for url in urls:
            try:
                resp = requests.head(url, allow_redirects=True, timeout=5)
                if resp.status_code != 200:
                    self.errors.append(f"Link check failed ({resp.status_code}): {url}")
                    return False
            except Exception as e:
                self.errors.append(f"Link check error for {url}: {e}")
                return False
        return True

    def _check_citations(self, text: str) -> bool:
        """Require at least 2 URLs as citations."""
        urls = re.findall(r'https?://\S+', text)
        if len(urls) < 2:
            self.errors.append("Citation count < 2")
            return False
        return True

    def _pii_detected(self, text: str) -> bool:
        """Basic PII regex: email or phone number."""
        email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
        phone_pattern = r'\b(?:\+?\d{1,3})?[-.\s]?(?:\(?\d{2,4}\)?)[-.\s]?\d{3,4}[-.\s]?\d{4}\b'
        if re.search(email_pattern, text) or re.search(phone_pattern, text):
            self.errors.append("PII detected in text")
            return True
        return False

    def _auto_confidence(self, record: Dict) -> str:
        """Assign confidence based on completeness of key fields."""
        filled_fields = sum(1 for k in ['description', 'category', 'impact', 'complexity', 'strategic_fit']
                            if record.get(k))
        if filled_fields >= 5:
            return "H"
        elif filled_fields >= 3:
            return "M"
        else:
            return "L"

    def run(self) -> List[Dict]:
        if not self.records:
            print("[ValidationAgent] No records provided for validation.")
            return []

        validated_records = []
        for idx, rec in enumerate(self.records, start=1):
            try:
                # Schema validation
                _ = NewUseCaseRecord(**rec)  # raises if invalid

                desc_text = rec.get("description", "")
                # Link check
                self._check_links(desc_text)
                # Citation count check
                self._check_citations(desc_text)
                # PII check
                self._pii_detected(desc_text)
                # Auto confidence if missing
                if not rec.get("confidence"):
                    rec["confidence"] = self._auto_confidence(rec)

                validated_records.append(rec)
            except Exception as e:
                self.errors.append(f"Record {idx} failed schema validation: {e}")

        if self.errors:
            print(f"[ValidationAgent] Completed with {len(self.errors)} issues found.")
        else:
            print("[ValidationAgent] All records passed validation.")

        return validated_records