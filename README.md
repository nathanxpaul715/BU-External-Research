# Multi-Agent Research Automation Pipeline  
*(LangGraph + Anthropic Claude + AWS)*

## 📌 Overview

This project implements the **BU-Research-Automation-v1.0** multi-stage research and synthesis pipeline, as described in the business requirements document.

The pipeline automates:
- **External Web Research** (Anthropic Claude Sonnet / Opus 4 + optional search APIs)
- **Internal Document Normalization** (DOCX/PDF with layout-aware extraction)
- **Synthesis** (combining external + internal into enterprise-grade insights)
- **Report Generation** (TXT for MVP; extendable to DOCX/PDF/XLSX)
- **Budget & Version Control** (approval gates and prompt compatibility checks)

Stages:
1. **Stage 0** — Supervisor Checks (budgets, prompt versions)
2. **Stage 1** — External Research
3. **Stage 2** — Internal Data Normalization
4. **Stage 3** — Synthesis
5. **Stage 4** — Report Writing

---

## 📂 Project Structure

research-pipeline/
├── agents/
│ ├── external_research_agent.py
│ ├── internal_data_agent.py
│ ├── synthesis_agent.py
│ ├── report_writer_agent.py
│ └── supervisor_agent.py
├── orchestrator/
│ └── pipeline_workflow.py
├── utils/
│ ├── chunking.py
│ ├── normalization.py
│ ├── budget_checks.py
│ └── prompt_validation.py
├── config/
│ ├── settings.py
│ └── prompt_compatibility_matrix.json
├── outputs/ # Generated reports
├── tests/ # Unit/integration tests
├── requirements.txt
├── run_pipeline.py # CLI Entry point
├── README.md
└── .env


---

## ⚙ Installation
1. Clone this repository  
2. Install dependencies: 
    pip install -r requirements.txt
3. Create a `.env` file with:
    ANTHROPIC_API_KEY=your_api_key_here
    AWS_ACCESS_KEY_ID=your_access_key
    AWS_SECRET_ACCESS_KEY=your_secret
    AWS_REGION=us-east-1
4. Ensure `outputs/` directory exists.

---

## ▶ Usage

### Run from CLI:
    python run_pipeline.py
    --topic "AI in Marketing"
    --function "Marketing"
    --internal_file_path "/path/to/internal.docx"
    --output_name "ai_marketing_baseline"

### Pipeline Flow:
1. **Budget & prompt version checks** (Stage 0)
2. **External research** via Anthropic Claude (Stage 1)
3. **Internal document normalization** (Stage 2)
4. **Merging & synthesis** of findings (Stage 3)
5. **Report generation** into `./outputs/` (Stage 4)

---

## 💡 Extending the MVP
- **Web Search Integration**: Plug in Serper.dev, Tavily, or Bing Search at Stage 1.
- **Deliverable Formats**: Use `python-docx`, `reportlab`, or `openpyxl` to output Word/PDF/Excel.
- **Stage Control**: Modify `run_pipeline()` to skip/execute specific stages.
- **Cost Tracking**: Integrate LangChain token/cost tracking for real usage billing.

---

## ✅ Non-Functional Requirements Implemented
- **Token Safety & Chunking**: via `RecursiveCharacterTextSplitter`  
- **Approval Gates** and **Budget Caps**
- **Prompt Version Control** via compatibility matrix
- **Strict Schema & Validation** before runs
- **Cloud Ready**: AWS-compatible for internal doc access

---

## 📜 License
*(Add license terms here)*
