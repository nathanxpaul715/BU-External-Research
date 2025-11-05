# tools/generation_tools.py  
"""  
Use Case Generation Tools for LangChain Agents  
"""
  
from langchain_core.tools import Tool 
from typing import List, Dict  
import json  
from config.config_tr_auth import get_anthropic_client, ANTHROPIC_MODEL
  
def generate_use_cases_batch_tool(  
    sub_function_name: str,  
    activities: List[Dict],  
    bu_context: str,  
    uc_counter: int  
) -> List[Dict]:  
    """Generate 8 use cases using Claude Sonnet 4.5"""
      
    client = get_anthropic_client()
      
    # Build activities text  
    activities_text = "\n".join([  
        f"{i+1}. {a['activity']} (Time: {a['time_spent_pct']}%, Tools: {a['current_tools']})"   
        for i, a in enumerate(activities)  
    ])
      
    # Generate abbreviation  
    abbrev = ''.join([c for c in sub_function_name if c.isupper()])[:4]  
    if not abbrev:  
        abbrev = sub_function_name[:4].upper()
      
    uc_start = uc_counter + 1  
    uc_end = uc_counter + 8
      
    prompt = f"""Generate 8 AI/ML use cases for **{sub_function_name}** sub-function.
  
**BUSINESS CONTEXT:**  
{bu_context[:1500]}
  
**ACTIVITIES (Top 8):**  
{activities_text}
  
**OUTPUT:** JSON array with 8 use cases, each with 27 columns.
  
Use Case IDs: UC-{abbrev}-{uc_start:03d} through UC-{abbrev}-{uc_end:03d}
  
Required columns: use_case_id, use_case_title, functional_non_functional, company, status, detailed_description, ai_technology, business_impact, business_impact_category, solution_complexity, implementation_complexity, implementation_priority, target_process_area, current_tools, impacted_roles, impacted_activities, current_tool_adaptation, adaptation_to_marketing, implementation_insights, risks_mitigations, industry_alignment, success_metrics, source_publication, source_url, source_date, information_gaps, sub_function
  
Return ONLY valid JSON array."""
      
    try:  
        response = client.messages.create(  
            model=ANTHROPIC_MODEL,  
            max_tokens=16000,  
            temperature=0.1,  
            messages=[{"role": "user", "content": prompt}]  
        )
          
        response_text = response.content[0].text
          
        if "```json" in response_text:  
            response_text = response_text.split("```json")[1].split("```")[0].strip()  
        elif "```" in response_text:  
            response_text = response_text.split("```")[1].split("```")[0].strip()
          
        use_cases = json.loads(response_text)  
        return use_cases  
    except Exception as e:  
        raise Exception(f"Failed to generate use cases: {e}")

  
def create_generation_tools():  
    """Create LangChain use case generation tools"""  
    return [  
        Tool(  
            name="generate_use_cases_batch",  
            func=lambda args: generate_use_cases_batch_tool(  
                args['sub_function_name'],  
                args['activities'],  
                args['bu_context'],  
                args['uc_counter']  
            ),  
            description="Generates 8 use cases with Claude Sonnet 4.5. Input: {'sub_function_name': str, 'activities': List[Dict], 'bu_context': str, 'uc_counter': int}. Returns: List[Dict] of 8 use cases."  
        )  
    ]