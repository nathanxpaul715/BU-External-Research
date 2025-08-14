# orchestrator/pipeline_workflow.py
from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph

# Stage 0
from agents.supervisor_agent import SupervisorAgent
# Stage 1
from agents.external_research_agent import ExternalResearchAgent
from agents.gap_analysis_agent import GapAnalysisAgent
# Stage 2
from agents.internal_data_agent import InternalDataAgent
from agents.enrichment_agent import EnrichmentAgent
# Stage 3
from agents.new_use_case_agent import NewUseCaseAgent
from agents.dedup_agent import DedupAgent
from agents.validation_agent import ValidationAgent
from agents.prioritization_agent import PrioritizationAgent
# Stage 4
from agents.report_writer_agent import ReportWriterAgent

class PipelineState(TypedDict):
    params: Dict[str, Any]
    budget: Dict[str, float]
    approvals: Dict[str, bool]
    prompt_versions: Dict[str, str]
    outputs: Dict[str, Any]
    errors: List[str]

def build_pipeline() -> StateGraph:
    graph = StateGraph(PipelineState)

    # Stage 0 L2
    def stage0_supervisor(state: PipelineState):
        SupervisorAgent(
            budget=state["budget"],
            approvals=state["approvals"],
            stage_prompt_versions=state["prompt_versions"]
        ).run()
        return state

    # Stage 1
    def stage1_external(state: PipelineState):
        ext_result = ExternalResearchAgent(
            topic=state["params"]["topic"],
            business_function=state["params"]["function"]
        ).run()
        state["outputs"]["stage1_external"] = ext_result
        return state

    def stage1_gap(state: PipelineState):
        gap_result = GapAnalysisAgent(
            manual_input=state["params"].get("stage1_manual", ""),
            automated_input=state["outputs"]["stage1_external"]
        ).run()
        state["outputs"]["stage1_gap"] = gap_result
        return state

    # Stage 2
    def stage2_internal(state: PipelineState):
        internal_text = InternalDataAgent(
            file_path=state["params"]["internal_file_path"]
        ).run()
        state["outputs"]["stage2_internal_text"] = internal_text
        return state

    def stage2_enrichment(state: PipelineState):
        enrich_path = EnrichmentAgent(
            internal_text=state["outputs"]["stage2_internal_text"]
        ).run()
        state["outputs"]["stage2_enrichment_file"] = enrich_path
        return state

    # Stage 3
    def stage3_new_use_cases(state: PipelineState):
        new_cases_path = NewUseCaseAgent(
            target_core=30,
            target_noncore=10,
            batch_size=5
        ).run()
        state["outputs"]["stage3_new_cases_file"] = new_cases_path
        return state

    def stage3_dedup(state: PipelineState):
        from pandas import read_excel
        records = read_excel(state["outputs"]["stage3_new_cases_file"]).to_dict(orient="records")
        deduped = DedupAgent(records).run()
        state["outputs"]["stage3_deduped"] = deduped
        return state

    def stage3_validate(state: PipelineState):
        validated = ValidationAgent(state["outputs"]["stage3_deduped"]).run()
        state["outputs"]["stage3_validated"] = validated
        return state

    def stage3_prioritize(state: PipelineState):
        prioritized = PrioritizationAgent(state["outputs"]["stage3_validated"]).run()
        state["outputs"]["stage3_prioritized"] = prioritized
        return state

    # Stage 4
    def stage4_writer(state: PipelineState):
        blueprint_path = ReportWriterAgent(
            prioritized_records=state["outputs"]["stage3_prioritized"],
            output_basename=state["params"].get("output_name", "stage4_blueprint")
        ).run()
        state["outputs"]["stage4_blueprint_path"] = blueprint_path
        return state

    # Nodes
    graph.add_node("stage0_supervisor", stage0_supervisor)
    graph.add_node("stage1_external", stage1_external)
    graph.add_node("stage1_gap", stage1_gap)
    graph.add_node("stage2_internal", stage2_internal)
    graph.add_node("stage2_enrichment", stage2_enrichment)
    graph.add_node("stage3_new_use_cases", stage3_new_use_cases)
    graph.add_node("stage3_dedup", stage3_dedup)
    graph.add_node("stage3_validate", stage3_validate)
    graph.add_node("stage3_prioritize", stage3_prioritize)
    graph.add_node("stage4_writer", stage4_writer)

    # Edges
    graph.set_entry_point("stage0_supervisor")
    graph.add_edge("stage0_supervisor", "stage1_external")
    graph.add_edge("stage1_external", "stage1_gap")
    graph.add_edge("stage1_gap", "stage2_internal")
    graph.add_edge("stage2_internal", "stage2_enrichment")
    graph.add_edge("stage2_enrichment", "stage3_new_use_cases")
    graph.add_edge("stage3_new_use_cases", "stage3_dedup")
    graph.add_edge("stage3_dedup", "stage3_validate")
    graph.add_edge("stage3_validate", "stage3_prioritize")
    graph.add_edge("stage3_prioritize", "stage4_writer")

    return graph

def run_pipeline(params: Dict[str, Any]):
    workflow = build_pipeline().compile()
    init_state: PipelineState = {
        "params": params,
        "budget": params.get("budget", {}),
        "approvals": params.get("approvals", {}),
        "prompt_versions": params.get("prompt_versions", {}),
        "outputs": {},
        "errors": []
    }
    return workflow.invoke(init_state)