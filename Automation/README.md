# Automation

**Centralized folder for all BU-External-Research automation scripts and systems.**

---

## 📁 Structure

```
Automation/
│
├── Business_Units/
│   └── Marketing/
│       └── Stage2_Marketing/        # Stage 2 automation for Marketing BU
│           ├── agents/              # 5 AI agents
│           ├── docs/                # Documentation
│           ├── config.py            # Configuration
│           ├── orchestrator.py      # Orchestrator
│           ├── run_automation.bat   # ⭐ Run script
│           └── README.md            # Documentation
│
└── README.md                        # This file
```

---

## 🎯 Purpose

This folder contains all automation code for the BU External Research project:
- **Separation of concerns**: Code here, data in `../data/`
- **Organization**: Organized by Business Unit and Stage
- **Scalability**: Easy to add new BUs and stages
- **Clean structure**: No mixing of automation and data files

---

## 📦 Current Automations

### Business_Units/Marketing/Stage2_Marketing
**Purpose**: Enrich Marketing AI use cases to premium consulting quality

**What it does**:
- Reads BU Intelligence and use cases from `../../data/`
- Uses 5 AI agents to enrich with 6 sections, 24 sub-headings
- Generates formatted Excel output
- Premium consulting-grade quality

**How to run**:
```bash
cd Business_Units/Marketing/Stage2_Marketing
run_automation.bat
```

**Documentation**: See [Business_Units/Marketing/Stage2_Marketing/README.md](Business_Units/Marketing/Stage2_Marketing/README.md)

---

## 🌟 Design Principles

1. **Clean Separation**
   - Automation code → `Automation/`
   - Data files → `data/`
   - Virtual environment → `venv/` (at root, shared)

2. **Organized by Business Unit**
   - `Business_Units/Marketing/` - Marketing automations
   - `Business_Units/Finance/` - Finance automations (future)
   - `Business_Units/Legal/` - Legal automations (future)

3. **Organized by Stage**
   - `Stage2_Marketing/` - Stage 2 for Marketing
   - `Stage3_Marketing/` - Stage 3 for Marketing (future)
   - etc.

4. **Scalable**
   - Easy to add new business units
   - Easy to add new stages
   - No code duplication

---

## 🔧 Shared Resources

**Virtual Environment**: `../venv/`
- Shared across all automations
- No duplication
- Install once, use everywhere

**Dependencies**: Each automation has its own `requirements.txt`
- Install specific packages per automation
- Run `setup_venv.bat` in each automation folder

---

## 📚 Adding New Automations

### Add new Business Unit (e.g., Finance):
```
Automation/Business_Units/Finance/Stage2_Finance/
```

### Add new Stage for existing BU:
```
Automation/Business_Units/Marketing/Stage3_Marketing/
```

**Template structure**:
```
{BU}/Stage{N}_{BU}/
├── agents/
├── docs/
├── config.py
├── orchestrator.py
├── run_automation.py
├── run_automation.bat
├── setup_venv.bat
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Access

| Automation | Location | Run Command |
|------------|----------|-------------|
| Marketing Stage 2 | `Business_Units/Marketing/Stage2_Marketing/` | `cd Business_Units/Marketing/Stage2_Marketing && run_automation.bat` |
| (Future) Finance Stage 2 | `Business_Units/Finance/Stage2_Finance/` | `cd Business_Units/Finance/Stage2_Finance && run_automation.bat` |
| (Future) Legal Stage 2 | `Business_Units/Legal/Stage2_Legal/` | `cd Business_Units/Legal/Stage2_Legal && run_automation.bat` |

---

## 🎨 Benefits

✅ **Organized by BU**: Each business unit has its own folder
✅ **Clean**: Separate from data files
✅ **Professional**: Logical folder hierarchy
✅ **Scalable**: Easy to expand
✅ **Maintainable**: Easy to find and update
✅ **Efficient**: Shared venv, no duplication

---

## 📝 Notes

- Each automation folder is self-contained
- All read from `../../data/` and write back to `../../data/`
- Virtual environment is shared at `../../venv/`
- Documentation in each automation's README

---

**Professional automation structure for BU External Research** 🚀
