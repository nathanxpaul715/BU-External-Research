# tools/validation_tools.py  
"""  
Validation and Export Tools for LangChain Agents  
"""
  
from langchain_core.tools import Tool
from typing import List, Dict  
import pandas as pd  
from datetime import datetime
  
def validate_use_case_tool(use_case: Dict) -> Dict:  
    """Validate a single use case for 27-column schema"""  
    required_columns = [  
        'use_case_id', 'use_case_title', 'functional_non_functional',   
        'company', 'status', 'detailed_description', 'ai_technology',  
        'business_impact', 'business_impact_category', 'solution_complexity',  
        'implementation_complexity', 'implementation_priority',   
        'target_process_area', 'current_tools', 'impacted_roles',  
        'impacted_activities', 'current_tool_adaptation',   
        'adaptation_to_marketing', 'implementation_insights',  
        'risks_mitigations', 'industry_alignment', 'success_metrics',  
        'source_publication', 'source_url', 'source_date',  
        'information_gaps', 'sub_function'  
    ]
      
    missing_cols = [col for col in required_columns if col not in use_case]
      
    return {  
        "valid": len(missing_cols) == 0,  
        "missing_columns": missing_cols  
    }

  
def export_to_excel_tool(use_cases: List[Dict], total_sub_functions: int) -> str:  
    """Export use cases to Excel"""  
    df = pd.DataFrame(use_cases)
      
    required_columns = [  
        'use_case_id', 'use_case_title', 'functional_non_functional',   
        'company', 'status', 'detailed_description', 'ai_technology',  
        'business_impact', 'business_impact_category', 'solution_complexity',  
        'implementation_complexity', 'implementation_priority',   
        'target_process_area', 'current_tools', 'impacted_roles',  
        'impacted_activities', 'current_tool_adaptation',   
        'adaptation_to_marketing', 'implementation_insights',  
        'risks_mitigations', 'industry_alignment', 'success_metrics',  
        'source_publication', 'source_url', 'source_date',  
        'information_gaps', 'sub_function'  
    ]
      
    for col in required_columns:  
        if col not in df.columns:  
            df[col] = ""
      
    df = df[required_columns]
      
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  
    output_file = f"Generated_Use_Cases_LangGraph_{timestamp}.xlsx"
      
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:  
        df.to_excel(writer, sheet_name='Use Cases', index=False)
          
        workbook = writer.book  
        worksheet = writer.sheets['Use Cases']
          
        header_format = workbook.add_format({  
            'bold': True,  
            'bg_color': '#4472C4',  
            'font_color': 'white',  
            'border': 1  
        })
          
        for col_num, value in enumerate(df.columns.values):  
            worksheet.write(0, col_num, value, header_format)
          
        for i, col in enumerate(df.columns):  
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2  
            worksheet.set_column(i, i, min(max_len, 60))
          
        worksheet.freeze_panes(1, 0)
      
    return output_file

  
def create_validation_tools():  
    """Create LangChain validation and export tools"""  
    return [  
        Tool(  
            name="validate_use_case",  
            func=validate_use_case_tool,  
            description="Validates use case for 27-column schema. Input: use_case (Dict). Returns: Dict with validation report."  
        ),  
        Tool(  
            name="export_to_excel",  
            func=lambda args: export_to_excel_tool(args['use_cases'], args['total_sub_functions']),  
            description="Exports use cases to Excel. Input: {'use_cases': List[Dict], 'total_sub_functions': int}. Returns: str (file path)."  
        )  
    ]