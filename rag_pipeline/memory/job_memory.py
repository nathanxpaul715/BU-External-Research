"""
Job Memory System
Implements lightweight context preservation from architecture section 7.7
Maintains state across stages with progressive compression
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from ..config.settings import JobMemoryConfig


@dataclass
class StageCompletion:
    """Record of completed stage"""
    stage: int
    completed_at: str
    key_findings: List[str]
    coverage: Dict[str, Any]
    quality_score: float
    cost: float


@dataclass
class JobMemory:
    """
    Job Memory Structure from architecture section 7.7
    Provides lightweight, token-efficient context preservation
    """
    job_id: str
    created_at: str
    updated_at: str
    executive_summary: str
    completed_stages: List[StageCompletion]
    current_stage: Dict[str, Any]
    gaps_identified: List[str]
    constraints: Dict[str, Any]
    risks: List[str]
    costs_by_stage: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "job_id": self.job_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "executive_summary": self.executive_summary,
            "completed_stages": [asdict(s) for s in self.completed_stages],
            "current_stage": self.current_stage,
            "gaps_identified": self.gaps_identified,
            "constraints": self.constraints,
            "risks": self.risks,
            "costs_by_stage": self.costs_by_stage
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class JobMemoryManager:
    """
    Manages job memory with progressive compression
    Implements algorithm from architecture section 7.7
    """

    def __init__(
        self,
        job_id: str,
        config: Optional[JobMemoryConfig] = None
    ):
        """
        Initialize job memory manager

        Args:
            job_id: Unique job identifier
            config: Job memory configuration
        """
        self.job_id = job_id
        self.config = config or JobMemoryConfig()

        # Initialize memory
        self.memory = JobMemory(
            job_id=job_id,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            executive_summary="Job initialized",
            completed_stages=[],
            current_stage={
                "stage": 0,
                "status": "in_progress",
                "percentage_complete": 0
            },
            gaps_identified=[],
            constraints={
                "budget_limit": 200.0,
                "budget_used": 0.0,
                "time_limit_hours": 12,
                "time_elapsed_hours": 0.0
            },
            risks=[],
            costs_by_stage={}
        )

    def update_executive_summary(self, summary: str):
        """
        Update executive summary

        Args:
            summary: New summary text
        """
        self.memory.executive_summary = summary
        self.memory.updated_at = datetime.now().isoformat()

    def complete_stage(
        self,
        stage: int,
        key_findings: List[str],
        coverage: Dict[str, Any],
        quality_score: float,
        cost: float
    ):
        """
        Record stage completion

        Args:
            stage: Stage number
            key_findings: List of key findings
            coverage: Coverage metrics
            quality_score: Quality score (0-100)
            cost: Stage cost in USD
        """
        completion = StageCompletion(
            stage=stage,
            completed_at=datetime.now().isoformat(),
            key_findings=key_findings,
            coverage=coverage,
            quality_score=quality_score,
            cost=cost
        )

        self.memory.completed_stages.append(completion)
        self.memory.costs_by_stage[f"stage_{stage}"] = cost

        # Update constraints
        total_cost = sum(self.memory.costs_by_stage.values())
        self.memory.constraints["budget_used"] = total_cost

        # Update time elapsed
        start_time = datetime.fromisoformat(self.memory.created_at)
        elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
        self.memory.constraints["time_elapsed_hours"] = round(elapsed_hours, 2)

        # Update risks
        self._update_risks()

        self.memory.updated_at = datetime.now().isoformat()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Stage {stage} completed")
        print(f"  Quality Score: {quality_score:.1f}")
        print(f"  Cost: ${cost:.2f}")
        print(f"  Total Cost: ${total_cost:.2f}")

    def update_current_stage(
        self,
        stage: int,
        status: str = "in_progress",
        percentage_complete: float = 0,
        **kwargs
    ):
        """
        Update current stage progress

        Args:
            stage: Stage number
            status: Stage status
            percentage_complete: Completion percentage
            **kwargs: Additional stage-specific data
        """
        self.memory.current_stage = {
            "stage": stage,
            "status": status,
            "percentage_complete": percentage_complete,
            **kwargs
        }
        self.memory.updated_at = datetime.now().isoformat()

    def add_gap(self, gap: str):
        """
        Add identified gap

        Args:
            gap: Gap description
        """
        if gap not in self.memory.gaps_identified:
            self.memory.gaps_identified.append(gap)
            self.memory.updated_at = datetime.now().isoformat()

    def add_risk(self, risk: str):
        """
        Add risk

        Args:
            risk: Risk description
        """
        if risk not in self.memory.risks:
            self.memory.risks.append(risk)
            self.memory.updated_at = datetime.now().isoformat()

    def _update_risks(self):
        """Update risk assessments based on current state"""
        self.memory.risks = []

        # Budget risk
        budget_used = self.memory.constraints.get("budget_used", 0)
        budget_limit = self.memory.constraints.get("budget_limit", 200)
        budget_pct = (budget_used / budget_limit * 100) if budget_limit > 0 else 0

        if budget_pct > 90:
            self.memory.risks.append(f"Budget risk: CRITICAL ({budget_pct:.0f}% used)")
        elif budget_pct > 75:
            self.memory.risks.append(f"Budget risk: HIGH ({budget_pct:.0f}% used)")
        elif budget_pct > 50:
            self.memory.risks.append(f"Budget risk: MEDIUM ({budget_pct:.0f}% used)")

        # Time risk
        time_elapsed = self.memory.constraints.get("time_elapsed_hours", 0)
        time_limit = self.memory.constraints.get("time_limit_hours", 12)
        time_pct = (time_elapsed / time_limit * 100) if time_limit > 0 else 0

        if time_pct > 90:
            self.memory.risks.append(f"Time risk: CRITICAL ({time_pct:.0f}% elapsed)")
        elif time_pct > 75:
            self.memory.risks.append(f"Time risk: HIGH ({time_pct:.0f}% elapsed)")

        # Quality risk
        if self.memory.completed_stages:
            avg_quality = sum(s.quality_score for s in self.memory.completed_stages) / len(self.memory.completed_stages)
            if avg_quality < 80:
                self.memory.risks.append(f"Quality risk: MEDIUM (avg score: {avg_quality:.1f})")

    def get_compressed_memory(self, max_tokens: Optional[int] = None) -> str:
        """
        Get progressively compressed memory for LLM context

        Args:
            max_tokens: Maximum tokens (default from config)

        Returns:
            Compressed memory string
        """
        max_tokens = max_tokens or self.config.max_memory_tokens

        if not self.config.enable_compression:
            return self.memory.to_json()

        # Build compressed summary
        compressed = []

        # Header
        compressed.append(f"JOB: {self.job_id}")
        compressed.append(f"STATUS: {self.memory.executive_summary}")
        compressed.append("")

        # Completed stages (condensed)
        if self.memory.completed_stages:
            compressed.append("COMPLETED STAGES:")
            for stage in self.memory.completed_stages:
                compressed.append(f"  Stage {stage.stage}: Quality {stage.quality_score:.0f}, Cost ${stage.cost:.2f}")
                if self.config.retain_key_findings and stage.key_findings:
                    # Keep only top 3 findings
                    for finding in stage.key_findings[:3]:
                        compressed.append(f"    - {finding}")
            compressed.append("")

        # Current stage
        current = self.memory.current_stage
        compressed.append(f"CURRENT: Stage {current.get('stage', 0)} ({current.get('percentage_complete', 0):.0f}% complete)")
        compressed.append("")

        # Gaps (if any)
        if self.memory.gaps_identified:
            compressed.append(f"GAPS: {len(self.memory.gaps_identified)} identified")
            for gap in self.memory.gaps_identified[:3]:  # Top 3
                compressed.append(f"  - {gap}")
            compressed.append("")

        # Constraints
        constraints = self.memory.constraints
        compressed.append("CONSTRAINTS:")
        if self.config.retain_cost_tracking:
            compressed.append(f"  Budget: ${constraints.get('budget_used', 0):.2f} / ${constraints.get('budget_limit', 200):.2f}")
        compressed.append(f"  Time: {constraints.get('time_elapsed_hours', 0):.1f}h / {constraints.get('time_limit_hours', 12)}h")
        compressed.append("")

        # Risks (if any)
        if self.memory.risks:
            compressed.append("RISKS:")
            for risk in self.memory.risks:
                compressed.append(f"  - {risk}")

        result = "\n".join(compressed)

        # Estimate tokens and truncate if needed
        estimated_tokens = len(result) // 4
        if estimated_tokens > max_tokens:
            # Aggressive truncation
            target_chars = max_tokens * 4
            result = result[:target_chars] + "\n[... truncated]"

        return result

    def get_full_memory(self) -> JobMemory:
        """Get full memory object"""
        return self.memory

    def save_to_file(self, file_path: str):
        """
        Save memory to JSON file

        Args:
            file_path: Output file path
        """
        with open(file_path, 'w') as f:
            json.dump(self.memory.to_dict(), f, indent=2)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Job memory saved to {file_path}")

    @classmethod
    def load_from_file(cls, file_path: str, config: Optional[JobMemoryConfig] = None):
        """
        Load memory from JSON file

        Args:
            file_path: Input file path
            config: Optional configuration

        Returns:
            JobMemoryManager instance
        """
        with open(file_path, 'r') as f:
            data = json.load(f)

        manager = cls(data['job_id'], config)

        # Restore memory
        manager.memory.created_at = data['created_at']
        manager.memory.updated_at = data['updated_at']
        manager.memory.executive_summary = data['executive_summary']
        manager.memory.completed_stages = [
            StageCompletion(**stage) for stage in data['completed_stages']
        ]
        manager.memory.current_stage = data['current_stage']
        manager.memory.gaps_identified = data['gaps_identified']
        manager.memory.constraints = data['constraints']
        manager.memory.risks = data['risks']
        manager.memory.costs_by_stage = data['costs_by_stage']

        return manager


# Convenience function
def create_job_memory(
    job_id: Optional[str] = None,
    config: Optional[JobMemoryConfig] = None
) -> JobMemoryManager:
    """
    Factory function to create job memory

    Args:
        job_id: Optional job ID (generates if not provided)
        config: Optional configuration

    Returns:
        JobMemoryManager instance
    """
    if not job_id:
        job_id = f"job-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    return JobMemoryManager(job_id, config)
