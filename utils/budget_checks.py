# utils/budget_checks.py
from config import settings

class BudgetError(Exception):
    """Raised when a stage exceeds budget without approval."""
    pass

def check_stage_budgets(budget: dict, approvals: dict):
    """
    Validate that each stage is within budget or has approval.

    Args:
        budget (dict): {stage_name: spend_in_usd}
        approvals (dict): {stage_name: bool}

    Raises:
        BudgetError: if any stage exceeds cap without approval
    """
    for stage, cap in settings.BUDGET_CAPS.items():
        stage_spend = budget.get(stage, 0)
        approved = approvals.get(stage, False)

        if stage_spend > cap and not approved:
            raise BudgetError(
                f"Stage {stage} exceeds budget (${stage_spend} vs cap ${cap}) "
                f"and no approval is recorded."
            )

def project_stage_costs(token_counts: dict, cost_per_1k_tokens: float):
    """
    Projects cost per stage from estimated token usage.

    Args:
        token_counts (dict): {stage_name: estimated_tokens}
        cost_per_1k_tokens (float): USD per 1000 tokens

    Returns:
        dict: {stage_name: projected_cost_usd}
    """
    projected = {}
    for stage, tokens in token_counts.items():
        projected[stage] = round((tokens / 1000) * cost_per_1k_tokens, 2)
    return projected

def is_within_budget(stage: str, cost: float, approvals: dict) -> bool:
    """
    Quick yes/no check for an individual stage.

    Args:
        stage (str): Stage ID
        cost (float): Cost in USD
        approvals (dict): {stage_name: bool}

    Returns:
        bool: True if within budget or approved.
    """
    cap = settings.BUDGET_CAPS.get(stage)
    approved = approvals.get(stage, False)

    if cap is None:
        return True
    if cost <= cap:
        return True
    return approved