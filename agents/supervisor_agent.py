# agents/supervisor_agent.py
from utils.budget_checks import check_stage_budgets, BudgetError
from utils.prompt_validation import validate_prompt_version, PromptVersionError

class SupervisorAgent:
    """
    Stage 0 L2 Supervisor Agent
    Enforces budgets and prompt version compatibility checks before executing pipeline stages.
    """

    def __init__(self, budget: dict, approvals: dict, stage_prompt_versions: dict):
        """
        Args:
            budget (dict): e.g., {"stage1": 10, "stage2": 15}
            approvals (dict): e.g., {"stage3": True}
            stage_prompt_versions (dict): e.g., {"stage1": "v1.0.2"}
        """
        self.budget = budget or {}
        self.approvals = approvals or {}
        self.stage_prompt_versions = stage_prompt_versions or {}

    def run(self) -> bool:
        """Run budget and prompt version checks. Raises if issues found."""
        print("[SupervisorAgent] Running Stage 0 L2 checks...")

        # 1. Budget enforcement
        try:
            check_stage_budgets(self.budget, self.approvals)
            print("[SupervisorAgent] ✅ Budget checks passed.")
        except BudgetError as e:
            print(f"[SupervisorAgent] ❌ Budget check failed: {e}")
            raise

        # 2. Prompt version compatibility
        for stage, version in self.stage_prompt_versions.items():
            try:
                validate_prompt_version(stage, version)
                print(f"[SupervisorAgent] ✅ Prompt version {version} valid for {stage}.")
            except PromptVersionError as e:
                print(f"[SupervisorAgent] ❌ Prompt compatibility failed: {e}")
                raise

        print("[SupervisorAgent] All pre-flight checks passed. Proceeding with pipeline.")
        return True