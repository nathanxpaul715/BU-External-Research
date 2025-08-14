# run_pipeline.py
import argparse
from orchestrator.pipeline_workflow import run_pipeline
from config import settings

def main():
    parser = argparse.ArgumentParser(description="Run Multi-Stage Research Pipeline (File Upload MVP)")
    parser.add_argument("--topic", required=True, help="Topic for external research")
    parser.add_argument("--function", required=True, help="Business function (e.g., Marketing)")
    parser.add_argument("--internal_file_path", required=True, help="Path to internal DOCX or PDF file")
    parser.add_argument("--output_name", default="stage4_blueprint", help="Base name for Stage 4 blueprint output")
    parser.add_argument("--stage1_manual", default="", help="Optional manual input for Stage 1 gap analysis")
    args = parser.parse_args()

    # Defaults from requirements doc — can be overridden later
    budgets = {
        "stage0_L2": 10,   # Below $15 cap
        "stage1": 20,      # Below $25 cap
        "stage2": 50,      # Below $60 cap
        "stage3": 150,     # Below $200 cap
        "stage4": 60       # Below $80 cap
    }
    approvals = {
        "stage0_L2": True,
        "stage1": True,
        "stage2": True,
        "stage3": True,
        "stage4": True
    }
    prompt_versions = {
        "stage0_L2": "v1.0.0",
        "stage1": "v1.0.0",
        "stage2": "v1.0.0",
        "stage3": "v1.0.0",
        "stage4": "v1.0.0"
    }

    params = {
        "topic": args.topic,
        "function": args.function,
        "internal_file_path": args.internal_file_path,
        "output_name": args.output_name,
        "stage1_manual": args.stage1_manual,
        "budget": budgets,
        "approvals": approvals,
        "prompt_versions": prompt_versions,
        "workspace_id": settings.WORKSPACE_ID,
        "external_model": settings.OPENAI_MODEL
    }

    print("[Main] Starting research pipeline run...")
    result_state = run_pipeline(params)

    print("\n[Main] Pipeline run complete.")
    if result_state["errors"]:
        print(f"[Main] Errors encountered: {result_state['errors']}")
    else:
        print(f"[Main] Success! Stage 4 blueprint: {result_state['outputs'].get('stage4_blueprint_path')}")

if __name__ == "__main__":
    main()