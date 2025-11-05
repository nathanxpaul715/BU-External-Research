"""
Quick Start Script for RAG-Enhanced Stage 2 Automation

This is a convenience wrapper around orchestrator_rag.py
"""
import sys
import os

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
marketing_dir = os.path.dirname(current_dir)  # Marketing
bu_dir = os.path.dirname(marketing_dir)  # Business_Units
automation_dir = os.path.dirname(bu_dir)  # Automation
project_root = os.path.dirname(automation_dir)  # Project root

sys.path.insert(0, current_dir)  # For orchestrator_rag
sys.path.insert(0, project_root)  # For rag_tool

from orchestrator_rag import main

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║            RAG-ENHANCED STAGE 2 AUTOMATION SYSTEM                            ║
║          AI Use Case Enrichment with RAG Integration                         ║
║                                                                              ║
║  This system uses 5 specialized agents enhanced with RAG:                   ║
║    1. RAG-Powered Context Builder                                           ║
║    2. RAG-Enhanced Web Research (with LLM summarization)                    ║
║    3. RAG-Enhanced Use Case Enricher                                        ║
║    4. Quality Assurance & Validation                                        ║
║    5. Output Formatter & Excel Generator                                    ║
║                                                                              ║
║  RAG Features:                                                               ║
║    ✓ Context from TR internal documents via FAISS vector store             ║
║    ✓ Gap analysis from knowledge base                                       ║
║    ✓ External market intelligence                                           ║
║    ✓ LLM-summarized web research (concise insights)                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Starting automation...
    """)

    main()
