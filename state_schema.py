# state_schema.py  
"""  
LangGraph State Schema  
Defines the shared state across all agents in the multi-agent workflow  
"""
  
from typing import TypedDict, List, Dict, Optional, Annotated  
from langgraph.graph.message import add_messages
  
class AgentState(TypedDict):  
    """  
    Shared state for the multi-agent workflow  
    This state is passed between all LangGraph nodes and maintains context across the entire execution  
    """
      
    # ========== INPUT FILES (Streamlit uploads) ==========  
    file1_path: str  # BU Intelligence document path (UPLOADED via Streamlit)  
    file3_path: str  # Role Activity Mapping Excel path (UPLOADED via Streamlit)  
    file5_path: Optional[str]  # Strategic Priorities (optional, UPLOADED via Streamlit)
      
    # ========== DATA FOLDER ==========  
    data_folder_path: str  # Path to data folder (default: "data/Business Units/Marketing/Stage 2")
      
    # ========== PARSED DATA ==========  
    bu_intelligence: str  # Parsed BU Intelligence text (from File 1)  
    enriched_use_cases: List[Dict]  # Existing use cases loaded from data folder (File 2)  
    sub_functions: List[str]  # List of all detected sub-functions (dynamically detected from File 3)  
    total_sub_functions: int  # Total count of sub-functions (for progress tracking)  
    strategic_priorities: Optional[Dict]  # Parsed File 5+ strategic priorities (if uploaded)
      
    # ========== PROCESSING STATE ==========  
    current_sub_function: Optional[str]  # Currently processing sub-function name  
    current_sub_function_index: int  # Index in sub_functions list (0 to N-1)  
    current_activities: List[Dict]  # Activities for current sub-function (top 8 by Time Spent %)  
    uc_counter: int  # Running UC ID counter for numbering (always starts from 0, no continuation)
      
    # ========== GENERATED OUTPUT ==========  
    generated_use_cases: List[Dict]  # All generated use cases (N sub-functions × 8 use cases)
      
    # ========== ROUTING FLAGS ==========  
    has_strategic_priorities: bool  # True if File 5+ uploaded (triggers strategic priority boost logic)  
    processing_complete: bool  # True when all sub-functions processed (triggers finalization)
      
    # ========== VALIDATION & OUTPUT ==========  
    validation_report: Optional[Dict]  # Validation results from Agent 3 (Output Assembler)  
    output_file_path: Optional[str]  # Path to generated Excel file (final output)
      
    # ========== AGENT MEMORY (LangChain) ==========  
    messages: Annotated[List, add_messages]  # Conversation history with Claude (for LangChain agent memory)
      
    # ========== ERROR HANDLING ==========  
    errors: List[str]  # Any errors encountered during processing (logged for debugging)