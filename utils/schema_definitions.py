# utils/schema_definitions.py
from pydantic import BaseModel
from typing import Optional

# Stage 2 enrichment schema columns
enrichment_columns = [
    "use_case_title", "description", "source", "category", "tags",
    "owner", "last_updated", "status"
]

class EnrichmentRecord(BaseModel):
    use_case_title: str
    description: str
    source: str
    category: str
    tags: Optional[str] = ""
    owner: Optional[str] = ""
    last_updated: Optional[str] = ""
    status: Optional[str] = ""

# utils/schema_definitions.py (add after enrichment schema)

new_use_case_columns = [
    "title", "description", "category", "impact", "complexity",
    "confidence", "strategic_fit", "type"
]

class NewUseCaseRecord(BaseModel):
    title: str
    description: str
    category: str
    impact: str
    complexity: str
    confidence: str
    strategic_fit: str
    type: str  # 'core' or 'non-core'