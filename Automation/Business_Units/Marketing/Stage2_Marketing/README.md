# Stage 2 Marketing Automation

**Clean, organized automation system for enriching Marketing AI use cases to premium consulting quality.**

---

## 📁 New Clean Structure

```
BU-External-Research/                    # Root
│
├── Automation/                          # ✨ All automation code here
│   └── Stage2_Marketing/                # Stage 2 for Marketing BU
│       ├── agents/                      # 5 AI agents
│       ├── docs/                        # Documentation
│       ├── config.py                    # Configuration
│       ├── orchestrator.py              # Main coordinator
│       ├── run_automation.py            # Python entry
│       ├── run_automation.bat           # ⭐ Double-click to run
│       ├── setup_venv.bat               # Setup packages
│       ├── requirements.txt             # Dependencies
│       └── README.md                    # This file
│
├── venv/                                # Virtual environment (shared)
│
└── data/                                # All data files
    └── Business Units/
        └── Marketing/
            ├── Input Files/             # Input CSVs
            ├── Stage 1/                 # BU Intelligence
            └── Stage 2/                 # Output Excel
```

---

## ✅ Clean Separation

| Folder | Purpose | What's Inside |
|--------|---------|---------------|
| `Automation/` | Code & scripts | Python agents, orchestrator, config |
| `data/` | Data files only | Input CSVs, BU docs, output Excel |
| `venv/` | Python packages | Virtual environment (shared) |

**No mixing! Clean and professional.**

---

## 🚀 How to Run

### Option 1: Double-Click (Easiest)
```
run_automation.bat
```

### Option 2: Command Line
```bash
# From Automation/Stage2_Marketing directory
..\..\venv\Scripts\python.exe run_automation.py
```

### Option 3: Fast Mode (Skip Web Research)
```bash
..\..\venv\Scripts\python.exe run_automation.py --skip-web-research
```

---

## 📊 What It Does

**Reads Data From**:
- `../../data/Business Units/Marketing/Stage 1/1b-MKTG-BU Intelligence.docx`
- `../../data/Business Units/Marketing/Input Files/MKTG_Current AI Use Cases_13.10.2025.csv`
- `../../data/Business Units/Marketing/Input Files/MKTG_Function Updates_13.10.2025.csv`

**Processes With**:
1. **Agent 1**: Data Ingestion & Context Builder
2. **Agent 2**: Web Research & Competitive Intelligence
3. **Agent 3**: Use Case Enricher (6 sections, 24 sub-headings)
4. **Agent 4**: Quality Assurance & Validation
5. **Agent 5**: Output Formatter & Excel Generator

**Writes Output To**:
- `../../data/Business Units/Marketing/Stage 2/2b-MKTG-Existing Use Cases Enriched.xlsx`

---

## 🎯 Output Quality

Each use case enriched with:

- **Detailed Description** (4 sub-headings)
- **Business Outcomes** (4 sub-headings)
- **Industry Alignment** (4 sub-headings, 2-3 competitors)
- **Implementation Considerations** (4 sub-headings)
- **Success Metrics/KPIs** (4 sub-headings)
- **Information Gaps & Annotation** (sources, confidence levels)

**Standards**: 3-5 quantified sentences per sub-heading, specific metrics, source citations

---

## ⚙️ Configuration

Edit `config.py` to customize:
- Input/output paths (currently set for Marketing)
- API settings (workspace ID, model)
- Processing parameters (batch size, tokens, web search)

---

## 🔧 First Time Setup

```bash
# Run setup to install packages
setup_venv.bat
```

This will:
1. Check for venv at `../../venv/`
2. Install all required packages:
   - anthropic
   - requests
   - python-docx
   - openpyxl
   - pandas

---

## ⏱️ Runtime

- **Full Mode** (with web research): 5-10 minutes
- **Fast Mode** (skip web research): 2-5 minutes

For 3 use cases

---

## 📚 Documentation

- [README.md](README.md) - This file
- [docs/README_STAGE2.md](docs/README_STAGE2.md) - Full documentation
- [docs/QUICKSTART_STAGE2.md](docs/QUICKSTART_STAGE2.md) - Quick start guide

---

## 🌟 Benefits of This Structure

✅ **Organized**: Automation code separate from data
✅ **Clean**: No mixing of code and data files
✅ **Scalable**: Easy to add Stage2_Finance, Stage2_Legal, etc.
✅ **Professional**: Clear, logical folder hierarchy
✅ **Maintainable**: Easy to find and update files
✅ **No Duplicates**: One venv at root, shared across all

---

## 🔄 File Relationships

```
Automation/Stage2_Marketing/          (automation code)
         ↓ reads from
data/Business Units/Marketing/        (input data)
         ↓ processes
agents/ (5 agents)
         ↓ writes to
data/Business Units/Marketing/Stage 2/ (output Excel)
```

---

## 🚧 Troubleshooting

### "Virtual environment not found"
- Run `setup_venv.bat`
- Or manually: `cd ../.. && python -m venv venv`

### "API key error"
- Check network connection
- Verify workspace ID in `config.py`

### "File not found"
- Check paths in `config.py`
- Ensure input files exist in `data/` folder

---

## 🎬 Quick Start

1. **First time**: Run `setup_venv.bat`
2. **Every time**: Double-click `run_automation.bat`
3. **Find output**: `../../data/Business Units/Marketing/Stage 2/2b-MKTG-Existing Use Cases Enriched.xlsx`

---

**Clean structure. Easy to use. Professional results.** 🚀
