# agents/file_orchestrator_agent.py  
"""  
AGENT 1: FILE ORCHESTRATOR AGENT  
Responsibilities:  
- Parse uploaded files (BU Intelligence, Role Activity Mapping)  
- Load Enriched Use Cases from data folder  
- Detect N sub-functions dynamically  
- Extract top 8 activities per sub-function  
"""
  
from tools.file_tools import (  
    detect_sub_functions_tool,  
    extract_activities_tool,  
    parse_bu_intelligence_tool,  
    load_existing_use_cases_tool  
)  
from typing import Dict, List
  
class FileOrchestratorAgent:  
    """Agent for file parsing and data extraction"""
      
    def __init__(self):  
        self.name = "File Orchestrator Agent"  
        print(f"🤖 {self.name} initialized")
      
    def parse_files(  
        self,  
        file1_path: str,  
        file3_path: str,  
        data_folder_path: str = "data/Business Units/Marketing/Stage 2"  
    ) -> Dict:  
        """  
        Parse all files and return structured data
          
        Args:  
            file1_path: BU Intelligence document path  
            file3_path: Role Activity Mapping Excel path  
            data_folder_path: Path to data folder with Enriched Use Cases
          
        Returns:  
            Dictionary with parsed data  
        """  
        print(f"\n{'='*70}")  
        print(f"🤖 {self.name} - PARSING FILES")  
        print(f"{'='*70}")
          
        try:  
            # Call tools directly  
            sub_functions = detect_sub_functions_tool(file3_path)  
            bu_context = parse_bu_intelligence_tool(file1_path)  
            existing_use_cases = load_existing_use_cases_tool(data_folder_path)
              
            parsed_data = {  
                'sub_functions': sub_functions,  
                'bu_context': bu_context,  
                'existing_use_cases': existing_use_cases,  
                'total_sub_functions': len(sub_functions),  
                'file3_path': file3_path  
            }
              
            print(f"\n✅ {self.name} - File parsing complete")  
            print(f"   Sub-functions detected: {len(sub_functions)}")  
            print(f"   BU context length: {len(bu_context)} characters")  
            print(f"   Existing use cases: {len(existing_use_cases)}")
              
            return parsed_data
              
        except Exception as e:  
            print(f"❌ {self.name} - Error parsing files: {e}")  
            raise
      
    def extract_activities_for_sub_function(  
        self,  
        file3_path: str,  
        sub_function_name: str  
    ) -> List[Dict]:  
        """Extract top 8 activities for a specific sub-function"""
          
        print(f"\n📊 {self.name} - Extracting activities for '{sub_function_name}'")
          
        try:  
            activities = extract_activities_tool(file3_path, sub_function_name)  
            print(f"   ✅ Extracted {len(activities)} activities")  
            return activities  
        except Exception as e:  
            print(f"   ❌ Error extracting activities: {e}")  
            return []