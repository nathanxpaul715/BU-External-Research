# tools/file_tools.py  
"""  
File Processing Tools for LangChain Agents  
Updated with data path: data/Business Units/Marketing/Stage 2  
"""
  
from langchain_core.tools import Tool 
import pandas as pd  
import docx  
from typing import List, Dict
import os
  
def detect_sub_functions_tool(file3_path: str) -> List[str]:  
    """  
    Detect all sub-functions from Role Activity Mapping Excel
      
    Args:  
        file3_path: Path to Role Activity Mapping Excel file
      
    Returns:  
        List of sub-function names (sheet names, excluding 'Summary')  
    """  
    try:  
        excel_file = pd.ExcelFile(file3_path)  
        all_sheets = excel_file.sheet_names
          
        # Exclude Summary sheet (case-insensitive)  
        sub_functions = [s for s in all_sheets if s.lower() != "summary"]
          
        print(f"✅ Detected {len(sub_functions)} sub-functions from {file3_path}")  
        print(f"   Sub-functions: {sub_functions}")
          
        return sub_functions  
    except Exception as e:  
        print(f"❌ Failed to detect sub-functions: {e}")  
        raise Exception(f"Failed to detect sub-functions: {e}")

  
def extract_activities_tool(file3_path: str, sheet_name: str) -> List[Dict]:  
    """  
    Extract top 8 activities by Time Spent % for a sub-function
      
    Args:  
        file3_path: Path to Role Activity Mapping Excel file  
        sheet_name: Sub-function sheet name
      
    Returns:  
        List of activity dictionaries with activity, time_spent_pct, current_tools  
    """  
    try:  
        df = pd.read_excel(file3_path, sheet_name=sheet_name)
          
        activities = []  
        for idx, row in df.iterrows():  
            activity = row.get("Activity", "")  
            time_spent = row.get("Estimated % of Time Spent", 0)  
            tools = row.get("Functional AI Tools (Applicable)", "")
              
            # Filter out invalid rows  
            if pd.notna(activity) and activity.strip() and activity.lower() not in ["total", "note", ""]:  
                activities.append({  
                    "activity": str(activity).strip(),  
                    "time_spent_pct": float(time_spent) if pd.notna(time_spent) else 0,  
                    "current_tools": str(tools) if pd.notna(tools) else "None"  
                })
          
        # Sort by time spent (descending), get top 8  
        activities = sorted(activities, key=lambda x: x['time_spent_pct'], reverse=True)[:8]
          
        print(f"✅ Extracted {len(activities)} activities from '{sheet_name}':")  
        for i, a in enumerate(activities, 1):  
            print(f"   {i}. {a['activity']} ({a['time_spent_pct']}% time, Tools: {a['current_tools']})")
          
        return activities  
    except Exception as e:  
        print(f"❌ Failed to extract activities from '{sheet_name}': {e}")  
        raise Exception(f"Failed to extract activities: {e}")

  
def parse_bu_intelligence_tool(file1_path: str) -> str:  
    """  
    Parse BU Intelligence document as text
      
    Args:  
        file1_path: Path to BU Intelligence Word document
      
    Returns:  
        Full document text  
    """  
    try:  
        doc = docx.Document(file1_path)  
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
          
        print(f"✅ Parsed BU Intelligence: {len(text)} characters from {file1_path}")
          
        return text  
    except Exception as e:  
        print(f"❌ Failed to parse BU Intelligence: {e}")  
        raise Exception(f"Failed to parse BU Intelligence: {e}")

  
def load_existing_use_cases_tool(data_folder_path: str = "data/Business Units/Marketing/Stage 2") -> List[Dict]:  
    """  
    Load existing use cases from Enriched Use Cases Excel in data folder
      
    Args:  
        data_folder_path: Path to data folder (default: "data/Business Units/Marketing/Stage 2")
      
    Returns:  
        List of existing use case dictionaries  
    """  
    # Expected file name  
    enriched_file_name = "2b-MKTG-Existing Use Cases Enriched.xlsx"  
    file2_path = os.path.join(data_folder_path, enriched_file_name)
      
    try:  
        # Check if exact file exists  
        if not os.path.exists(file2_path):  
            print(f"⚠️  Enriched Use Cases file not found at: {file2_path}")  
            print(f"   Looking for alternative files in {data_folder_path}...")
              
            # Try to find any Excel file with "enriched" or "use case" in name  
            if os.path.exists(data_folder_path):  
                files = os.listdir(data_folder_path)  
                excel_files = [  
                    f for f in files   
                    if f.endswith('.xlsx') and ('enriched' in f.lower() or 'use case' in f.lower())  
                ]
                  
                if excel_files:  
                    file2_path = os.path.join(data_folder_path, excel_files[0])  
                    print(f"   ✅ Found alternative: {excel_files[0]}")  
                else:  
                    print(f"   ⚠️  No suitable Enriched Use Cases file found in {data_folder_path}")  
                    print(f"   Available files: {files}")  
                    return []  
            else:  
                print(f"   ❌ Data folder does not exist: {data_folder_path}")  
                print(f"   Please create folder: mkdir -p \"{data_folder_path}\"")  
                return []
          
        # Load Excel file  
        df = pd.read_excel(file2_path, sheet_name="Enriched Use Cases")  
        use_cases = df.to_dict('records')
          
        print(f"✅ Loaded {len(use_cases)} existing use cases from: {file2_path}")
          
        # Display first few use case titles for verification  
        if use_cases:  
            print(f"   Sample use cases:")  
            for i, uc in enumerate(use_cases[:3], 1):  
                title = uc.get('Enriched Use Case Name', uc.get('Original Use Case Name', 'Unknown'))  
                print(f"   {i}. {title}")
          
        return use_cases
          
    except FileNotFoundError:  
        print(f"⚠️  File not found: {file2_path}")  
        print(f"   Please ensure the file exists in: {data_folder_path}")  
        return []  
    except Exception as e:  
        print(f"⚠️  Could not load existing use cases from {file2_path}: {e}")  
        return []

  
def create_file_tools():  
    """  
    Create LangChain file processing tools
      
    Returns:  
        List of LangChain Tool objects  
    """  
    return [  
        Tool(  
            name="detect_sub_functions",  
            func=detect_sub_functions_tool,  
            description="""Detects all sub-functions from Role Activity Mapping Excel file.
              
Input: file3_path (str) - Path to Excel file  
Returns: List[str] of sub-function names (excludes 'Summary' sheet)
  
Example: detect_sub_functions("temp_file3.xlsx") → ["Demand Generation", "Product Marketing", ...]"""  
        ),  
        Tool(  
            name="extract_activities",  
            func=lambda args: extract_activities_tool(args['file3_path'], args['sheet_name']),  
            description="""Extracts top 8 activities by Time Spent % for a sub-function.
              
Input: {'file3_path': str, 'sheet_name': str}  
Returns: List[Dict] of activities with keys: activity, time_spent_pct, current_tools
  
Example: extract_activities({"file3_path": "temp_file3.xlsx", "sheet_name": "Demand Generation"})  
→ [{"activity": "Campaign Planning", "time_spent_pct": 70.0, "current_tools": "Writer"}, ...]"""  
        ),  
        Tool(  
            name="parse_bu_intelligence",  
            func=parse_bu_intelligence_tool,  
            description="""Parses BU Intelligence document and returns business context as text.
              
Input: file1_path (str) - Path to Word document  
Returns: str (full document text)
  
Example: parse_bu_intelligence("temp_file1.docx") → "EXECUTIVE SUMMARY\nThomson Reuters Marketing...\\"""  
        ),  
        Tool(  
            name="load_existing_use_cases",  
            func=load_existing_use_cases_tool,  
            description="""Loads existing use cases from Enriched Use Cases Excel in data folder.
              
Input: data_folder_path (str, optional) - Path to data folder (default: "data/Business Units/Marketing/Stage 2")  
Returns: List[Dict] of existing use cases for deduplication reference
  
Example: load_existing_use_cases("data/Business Units/Marketing/Stage 2")  
→ [{"Enriched Use Case Name": "Marketing Content Generation", ...}, ...]"""  
        )  
    ]