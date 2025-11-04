# Stage 2 Automation System

This automated system enriches AI use cases to premium consulting quality using 5 specialized AI agents.

## Overview

The Stage 2 automation takes your existing AI use cases and enriches them with:
- Detailed business context and problem analysis
- Quantified business outcomes and deliverables
- Competitive intelligence and vendor research
- Industry benchmarks and best practices
- Implementation considerations and risk assessment
- Success metrics (KPIs)
- Source citations and confidence levels

## System Architecture

### 5 Specialized Agents

1. **Agent 1: Data Ingestion & Context Builder**
   - Loads BU Intelligence document (632 paragraphs)
   - Loads AI Use Cases CSV
   - Loads Function Updates CSV
   - Extracts and structures business context

2. **Agent 2: Web Research & Competitive Intelligence**
   - Searches for competitor implementations
   - Researches vendor solutions and case studies
   - Finds industry benchmarks and analyst reports
   - Validates metrics with external sources
   - Provides source URLs and confidence levels

3. **Agent 3: Use Case Enricher**
   - Enriches each use case with 6 major sections
   - Uses 24 sub-headings across all sections
   - Generates 3-5 quantified sentences per sub-heading
   - Integrates BU Intelligence context
   - Incorporates web research findings

4. **Agent 4: Quality Assurance & Validation**
   - Validates all required sub-headings are present
   - Checks for quantified metrics and benchmarks
   - Verifies minimum 2-3 competitors/vendors cited
   - Validates source citations and confidence levels
   - Ensures consulting-grade quality standards

5. **Agent 5: Output Formatter & Excel Generator**
   - Formats enriched content with proper structure
   - Creates Excel file with 11 columns
   - Applies cell formatting (text wrapping, column widths)
   - Generates final output: `2b-MKTG-Existing Use Cases Enriched.xlsx`

### Agent Orchestration Flow

```
Agent 1 (Data Ingestion)
    ↓
Agent 2 (Web Research) + Agent 3 (Use Case Enricher) [Parallel]
    ↓
Agent 4 (Quality Assurance)
    ↓
Agent 5 (Output Formatter)
```

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

Required packages:
- anthropic (Claude API)
- requests (API calls)
- python-docx (Read Word documents)
- openpyxl (Excel generation)
- pandas (Data manipulation)

## Input Files Required

The system expects these files in the correct locations:

1. **BU Intelligence Document**:
   - Path: `data/Business Units/Marketing/Stage 1/1b-MKTG-BU Intelligence.docx`
   - Content: Business context, competitors, vendors, strategy

2. **AI Use Cases CSV**:
   - Path: `data/Business Units/Marketing/Input Files/MKTG_Current AI Use Cases_13.10.2025.csv`
   - Content: Use cases to be enriched

3. **Function Updates CSV**:
   - Path: `data/Business Units/Marketing/Input Files/MKTG_Function Updates_13.10.2025.csv`
   - Content: Recent updates and status

## Usage

### Basic Usage (Full Process with Web Research)
```bash
python run_stage2_automation.py
```

This runs all 5 agents including web research. Takes longer but produces more comprehensive results.

### Fast Mode (Skip Web Research)
```bash
python run_stage2_automation.py --skip-web-research
```

Skips Agent 2 (web research) for faster processing. Uses BU Intelligence and LLM knowledge only.

### Debug Mode
```bash
python run_stage2_automation.py --debug
```

Enables verbose output for troubleshooting.

## Output

The system generates:

**Output File**: `data/Business Units/Marketing/Stage 2/2b-MKTG-Existing Use Cases Enriched.xlsx`

**Output Columns** (11 total):
1. Function
2. Original Use Case Name
3. Enriched Use Case Name
4. Original Use Case Description
5. Detailed Enriched Use Case Description
6. Original Outcomes/Deliverable
7. Enriched Business Outcomes/Deliverables
8. Industry Alignment
9. Implementation Considerations
10. Suggested Success Metrics (KPIs)
11. Information Gaps & Annotation

Each enriched column contains structured content with sub-headings and bullet points.

## Configuration

Edit `stage2_automation/config.py` to customize:
- File paths
- API configuration
- Processing parameters (batch size, max tokens, web search limits)
- Output column definitions
- Sub-heading structure

## API Configuration

The system uses Thomson Reuters' internal Anthropic API proxy:
- **API URL**: `https://aiplatform.gcs.int.thomsonreuters.com/v1/anthropic/token`
- **Workspace ID**: `ExternalResei8Dz`
- **Model**: `claude-sonnet-4-20250514`

API credentials are fetched automatically from the test_api.py pattern.

## Quality Standards

The system enforces premium consulting-level quality:
- ✓ All required sub-headings present
- ✓ 3-5 substantive sentences per sub-heading
- ✓ Quantified metrics with sources
- ✓ Minimum 2-3 named competitors/vendors
- ✓ Source citations and confidence levels
- ✓ Consistent formatting throughout

## Troubleshooting

### Common Issues

1. **"Cannot access files"**
   - Check file paths in `config.py`
   - Ensure all input files exist

2. **"API key error"**
   - Verify workspace ID in `config.py`
   - Check network connection to TR internal API

3. **"Quality validation failed"**
   - Review QA output for specific issues
   - May need to adjust prompts in agent files

4. **"Out of memory/tokens"**
   - Reduce `MAX_TOKENS` in config.py
   - Enable batch processing with smaller `BATCH_SIZE`

## Development

### Project Structure
```
BU-External-Research/
├── stage2_automation/
│   ├── __init__.py
│   ├── config.py                  # Configuration
│   ├── agent1_data_ingestion.py   # Agent 1
│   ├── agent2_web_research.py     # Agent 2
│   ├── agent3_use_case_enricher.py # Agent 3
│   ├── agent4_quality_assurance.py # Agent 4
│   ├── agent5_output_formatter.py  # Agent 5
│   └── orchestrator.py            # Main orchestrator
├── run_stage2_automation.py       # Entry point
├── requirements.txt               # Dependencies
└── README_STAGE2.md              # This file
```

### Testing Individual Agents

Each agent can be tested independently:

```python
# Test Agent 1
from stage2_automation.agent1_data_ingestion import DataIngestionAgent
agent1 = DataIngestionAgent()
result = agent1.run()

# Test Agent 4 (with mock data)
from stage2_automation.agent4_quality_assurance import QualityAssuranceAgent
agent4 = QualityAssuranceAgent()
# ... provide enrichment data
```

## Performance

**Typical Runtime** (3 use cases):
- With web research: 5-10 minutes
- Without web research: 2-5 minutes

**Token Usage**:
- Per use case: ~5,000-8,000 tokens
- Total for 3 use cases: ~15,000-24,000 tokens

## Future Enhancements

Potential improvements:
- [ ] Parallel processing of multiple use cases
- [ ] Caching of web research results
- [ ] More sophisticated confidence scoring
- [ ] Integration with additional data sources
- [ ] Automated retry logic for failed enrichments
- [ ] Progress bars and real-time status updates
- [ ] Email notifications on completion
- [ ] Support for other business units

## Support

For issues or questions:
1. Check this README
2. Review error messages and logs
3. Check `test_api.py` for API connection issues
4. Contact the development team

## License

Internal Thomson Reuters use only.
