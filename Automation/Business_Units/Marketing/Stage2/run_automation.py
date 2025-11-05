"""
Stage 2 Automation - Main Entry Point

This script runs the complete Stage 2 automation process for enriching AI use cases.

Usage:
    python run_automation.py                    # Full process with web research
    python run_automation.py --skip-web-research # Faster, skip web research
    python run_automation.py --debug            # Debug mode with verbose output
"""
import sys
import os

# Add the automation directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator import main

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     STAGE 2 AUTOMATION SYSTEM                                ║
║                  AI Use Case Enrichment Automation                           ║
║                                                                              ║
║  This system automates the Stage 2 process using 5 specialized agents:      ║
║    1. Data Ingestion & Context Builder                                      ║
║    2. Web Research & Competitive Intelligence                               ║
║    3. Use Case Enricher                                                     ║
║    4. Quality Assurance & Validation                                        ║
║    5. Output Formatter & Excel Generator                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    main()
