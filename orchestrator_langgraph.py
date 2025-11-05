# orchestrator_langgraph.py  
"""  
MAIN LANGGRAPH ORCHESTRATOR  
Entry point for running the complete multi-agent workflow  
"""
  
from agents.supervisor_agent import SupervisorAgent  
from typing import Optional, Callable
  
def run_langgraph_workflow(  
    file1_path: str,  
    file3_path: str,  
    file5_paths: Optional[list] = None,  
    data_folder_path: str = "data/Business Units/Marketing/Stage 2",  
    progress_callback: Optional[Callable] = None  
) -> str:  
    """  
    Run the complete LangGraph multi-agent workflow
      
    Args:  
        file1_path: BU Intelligence document path  
        file3_path: Role Activity Mapping Excel path  
        file5_paths: List of Strategic Priority document paths (optional)  
        data_folder_path: Path to data folder with Enriched Use Cases  
        progress_callback: Optional callback for progress updates (current, total, sub_function_name)
      
    Returns:  
        Path to generated Excel file  
    """
      
    # Initialize supervisor agent  
    supervisor = SupervisorAgent()
      
    # Handle File 5+ (take first file if multiple uploaded)  
    file5_path = file5_paths[0] if file5_paths and len(file5_paths) > 0 else None
      
    # Run workflow  
    output_file = supervisor.run(  
        file1_path=file1_path,  
        file3_path=file3_path,  
        data_folder_path=data_folder_path,  
        file5_path=file5_path,  
        progress_callback=progress_callback  
    )
      
    return output_file  