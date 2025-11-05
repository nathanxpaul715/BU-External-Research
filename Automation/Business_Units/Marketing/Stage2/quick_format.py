"""
Quick formatter to create Excel output from Agent 2 web research data
"""
import json
import pandas as pd
from datetime import datetime

# Load Agent 2 output
agent2_path = r"c:\Users\6136942\OneDrive - Thomson Reuters Incorporated\Documents\bu_repo\BU-External-Research\Automation\data\Business Units\Marketing\Stage 2\agent_outputs\agent2_web_research_output.json"

with open(agent2_path, 'r', encoding='utf-8') as f:
    agent2_data = json.load(f)

# Format the data
rows = []
for result in agent2_data['research_results']:
    use_case = result['use_case_name']

    # Competitor Intelligence
    comp_intel = result['competitor_intelligence']
    comp_data = comp_intel.get('data', 'N/A')[:500] + "..." if comp_intel.get('success') else comp_intel.get('error', 'N/A')

    # Vendor Solutions
    vendor = result['vendor_solutions']
    vendor_data = vendor.get('data', 'N/A')[:500] + "..." if vendor.get('success') else vendor.get('error', 'N/A')

    # Industry Benchmarks
    benchmarks = result['industry_benchmarks']
    benchmark_data = benchmarks.get('data', 'N/A')[:500] + "..." if benchmarks.get('success') else benchmarks.get('error', 'N/A')

    rows.append({
        'Use Case Name': use_case,
        'Competitor Intelligence (Summary)': comp_data,
        'Vendor Solutions (Summary)': vendor_data,
        'Industry Benchmarks (Summary)': benchmark_data,
        'Research Completed': datetime.now().strftime('%Y-%m-%d %H:%M')
    })

# Create DataFrame
df = pd.DataFrame(rows)

# Save to Excel
output_path = r"c:\Users\6136942\OneDrive - Thomson Reuters Incorporated\Documents\bu_repo\BU-External-Research\data\Business Units\Marketing\Stage 2\2b-MKTG-Web_Research_Summary.xlsx"
df.to_excel(output_path, index=False, sheet_name='Web Research')

print(f"Excel file created: {output_path}")
print(f"Contains {len(rows)} use cases")
