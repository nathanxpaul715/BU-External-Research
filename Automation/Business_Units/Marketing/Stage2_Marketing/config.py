"""Configuration for Stage 2 Marketing Automation"""
import os

# Base paths - Automation folder is at root level
AUTOMATION_DIR = os.path.dirname(os.path.abspath(__file__))  # Automation/Business_Units/Marketing/Stage2_Marketing
# Go up 4 levels: Stage2_Marketing -> Marketing -> Business_Units -> Automation -> BU-External-Research
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(AUTOMATION_DIR))))
DATA_DIR = os.path.join(ROOT_DIR, "data", "Business Units", "Marketing")

# Input file paths
BU_INTELLIGENCE_PATH = os.path.join(DATA_DIR, "Stage 1", "1b-MKTG-BU Intelligence.docx")
USE_CASES_CSV_PATH = os.path.join(DATA_DIR, "Input Files", "MKTG_Current AI Use Cases_13.10.2025.csv")
FUNCTION_UPDATES_CSV_PATH = os.path.join(DATA_DIR, "Input Files", "MKTG_Function Updates_13.10.2025.csv")

# Optional files (if available)
OPTIONAL_FILES = {
    "internal_intelligence": os.path.join(DATA_DIR, "Input Files", "0b-CONCISE OUTPUT_Internal Company Intelligence.docx"),
    "gap_analysis": os.path.join(DATA_DIR, "Input Files", "0f-CONCISE OUTPUT_Internal-External Gap Analysis.docx")
}

# Output path
OUTPUT_PATH = os.path.join(DATA_DIR, "Stage 2", "2b-MKTG-Existing Use Cases Enriched.xlsx")

# Anthropic API configuration
ANTHROPIC_API_URL = "https://aiplatform.gcs.int.thomsonreuters.com/v1/anthropic/token"
WORKSPACE_ID = "ExternalResei8Dz"
MODEL = "claude-sonnet-4-20250514"

# Processing configuration
BATCH_SIZE = 5  # Process 5 use cases at a time if token limits apply
MAX_TOKENS = 8000  # Max tokens per API call
WEB_SEARCH_MAX_USES = 10  # Max web searches per enrichment

# Output column definitions
OUTPUT_COLUMNS = [
    "Function",
    "Original Use Case Name",
    "Enriched Use Case Name",
    "Original Use Case Description",
    "Detailed Enriched Use Case Description",
    "Original Outcomes/Deliverable",
    "Enriched Business Outcomes/Deliverables",
    "Industry Alignment",
    "Implementation Considerations",
    "Suggested Success Metrics (KPIs)",
    "Information Gaps & Annotation"
]

# Sub-heading structure for enrichment
SUB_HEADINGS = {
    "detailed_description": [
        "Business Context & Problem",
        "Solution & Technology",
        "Integration & Process",
        "Current Status & Outcomes"
    ],
    "business_outcomes": [
        "Productivity & Efficiency",
        "Quality & Consistency",
        "Cost & Financial Impact",
        "Strategic Benefits"
    ],
    "industry_alignment": [
        "Competitive Landscape",
        "Technology & Vendors",
        "Industry Benchmarks",
        "Strategic Positioning"
    ],
    "implementation": [
        "Technical & Integration",
        "Change Management",
        "Risk & Compliance",
        "Operational & Scaling"
    ],
    "kpis": [
        "Operational Metrics",
        "Financial Metrics",
        "Quality Metrics",
        "Strategic Metrics"
    ],
    "annotation": [
        "Source",
        "Confidence Level",
        "Rationale",
        "Information Gaps"
    ]
}
