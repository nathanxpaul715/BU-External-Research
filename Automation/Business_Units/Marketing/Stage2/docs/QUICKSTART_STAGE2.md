# Stage 2 Automation - Quick Start Guide

## ✅ Setup Complete!

All checks passed. Your Stage 2 automation system is ready to run.

## What This System Does

Automatically enriches **3 AI use cases** from the Marketing business unit with:
- Detailed business context and problem analysis
- Quantified outcomes with industry benchmarks
- Competitive intelligence (2-3 named competitors per use case)
- Vendor research and technology recommendations
- Implementation roadmap and risk assessment
- Success metrics (KPIs)
- Source citations and confidence levels

**Input**: 3 use cases from `MKTG_Current AI Use Cases_13.10.2025.csv`
**Output**: Fully enriched Excel file `2b-MKTG-Existing Use Cases Enriched.xlsx`

## Quick Start (3 Steps)

### Step 1: Choose Your Mode

**Option A: Full Mode (Recommended) - Using Virtual Environment**
```bash
venv\Scripts\python.exe run_stage2_automation.py
```
Or simply double-click: `run_with_venv.bat`

- Includes web research for competitive intelligence
- Most comprehensive results
- Takes 5-10 minutes

**Option B: Fast Mode - Using Virtual Environment**
```bash
venv\Scripts\python.exe run_stage2_automation.py --skip-web-research
```
- Skips web research
- Faster processing (2-5 minutes)
- Uses BU Intelligence + LLM knowledge only

**Note**: All packages are installed in the `venv` virtual environment to avoid conflicts.

### Step 2: Monitor Progress

The system will show progress as it runs through 5 agents:
```
🔄 Agent 1: Data Ingestion & Context Builder
🔄 Agent 2: Web Research & Competitive Intelligence (if enabled)
🔄 Agent 3: Use Case Enricher
🔄 Agent 4: Quality Assurance & Validation
🔄 Agent 5: Output Formatter & Excel Generator
```

### Step 3: Review Output

Find your enriched use cases here:
```
data/Business Units/Marketing/Stage 2/2b-MKTG-Existing Use Cases Enriched.xlsx
```

## What Gets Enriched

For each of the 3 use cases, the system generates:

### Column 5: Detailed Enriched Use Case Description
- Business Context & Problem
- Solution & Technology
- Integration & Process
- Current Status & Outcomes

### Column 7: Enriched Business Outcomes/Deliverables
- Productivity & Efficiency
- Quality & Consistency
- Cost & Financial Impact
- Strategic Benefits

### Column 8: Industry Alignment
- Competitive Landscape (2-3 competitors)
- Technology & Vendors (specific products)
- Industry Benchmarks (quantified metrics)
- Strategic Positioning

### Column 9: Implementation Considerations
- Technical & Integration
- Change Management
- Risk & Compliance
- Operational & Scaling

### Column 10: Suggested Success Metrics (KPIs)
- Operational Metrics
- Financial Metrics
- Quality Metrics
- Strategic Metrics

### Column 11: Information Gaps & Annotation
- Source (all references)
- Confidence Level (High/Medium/Low)
- Rationale (methodology)
- Information Gaps (missing data)

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Stage 2 Orchestrator                         │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Agent 1       │  │   Agent 2       │  │   Agent 3       │
│ Data Ingestion  │─▶│ Web Research    │─▶│ Use Case        │
│ - BU Intel      │  │ - Competitors   │  │   Enricher      │
│ - Use Cases     │  │ - Vendors       │  │ - 6 sections    │
│ - Context       │  │ - Benchmarks    │  │ - 24 sub-heads  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                                                   │
                              ┌────────────────────┴────────────────┐
                              ▼                                     ▼
                     ┌─────────────────┐                  ┌─────────────────┐
                     │   Agent 4       │                  │   Agent 5       │
                     │ Quality         │─────────────────▶│ Output          │
                     │   Assurance     │                  │   Formatter     │
                     │ - Validation    │                  │ - Excel Gen     │
                     │ - QA Checks     │                  │ - Formatting    │
                     └─────────────────┘                  └─────────────────┘
```

## Expected Output Format

Each use case will have:
- **3-5 quantified sentences** per sub-heading
- **Specific metrics** (percentages, dollar amounts, time savings)
- **Named competitors/vendors** (minimum 2-3)
- **Source citations** (BU Intelligence, web URLs, reports)
- **Confidence levels** (High/Medium/Low with rationale)

## Troubleshooting

### "API key error"
- Check your network connection
- Verify workspace ID in `stage2_automation/config.py`

### "File not found"
- Verify input files are in correct locations
- Run `python test_stage2_setup.py` to diagnose

### "Quality validation failed"
- Review the QA output for specific issues
- Some use cases may need manual review
- Check the Excel output - partial results are still saved

### Need help?
```bash
python test_stage2_setup.py  # Diagnose issues
```

## Files Created

```
BU-External-Research/
├── stage2_automation/           # Agent package
│   ├── agent1_data_ingestion.py
│   ├── agent2_web_research.py
│   ├── agent3_use_case_enricher.py
│   ├── agent4_quality_assurance.py
│   ├── agent5_output_formatter.py
│   ├── orchestrator.py
│   └── config.py
├── run_stage2_automation.py     # Main entry point
├── test_stage2_setup.py         # Setup validator
├── requirements.txt             # Dependencies
├── README_STAGE2.md             # Full documentation
└── QUICKSTART_STAGE2.md         # This file
```

## Next Steps

1. **Run it now**: `python run_stage2_automation.py`
2. **Review output**: Open the Excel file and review enriched content
3. **Customize**: Edit `config.py` to adjust parameters
4. **Extend**: Add more use cases to the input CSV

## Technical Details

- **Model**: Claude Sonnet 4 (claude-sonnet-4-20250514)
- **API**: Thomson Reuters internal Anthropic proxy
- **Token usage**: ~5,000-8,000 per use case
- **Total for 3 cases**: ~15,000-24,000 tokens
- **Runtime**: 5-10 minutes (full), 2-5 minutes (fast)

## Quality Standards

The system enforces premium consulting-level quality:
- ✓ All 24 required sub-headings present
- ✓ 3-5 substantive sentences per sub-heading
- ✓ Quantified metrics with sources
- ✓ Minimum 2-3 named competitors/vendors
- ✓ Source citations and confidence levels
- ✓ Consistent formatting throughout

---

**Ready to run?**
```bash
python run_stage2_automation.py
```

For detailed documentation, see [README_STAGE2.md](README_STAGE2.md)
