# test_file_tools.py  
from tools.file_tools import (  
    detect_sub_functions_tool,  
    extract_activities_tool,  
    parse_bu_intelligence_tool,  
    load_existing_use_cases_tool  
)
  
print("="*70)  
print("TESTING FILE TOOLS")  
print("="*70)
  
# Test 1: Load existing use cases from new path  
print("\n[TEST 1] Loading existing use cases from data folder...")  
try:  
    use_cases = load_existing_use_cases_tool("data/Business Units/Marketing/Stage 2")  
    print(f"✅ Loaded {len(use_cases)} use cases")  
except Exception as e:  
    print(f"❌ Error: {e}")
  
# Test 2: Detect sub-functions (requires your File 3)  
# print("\n[TEST 2] Detecting sub-functions...")  
# try:  
#     sub_functions = detect_sub_functions_tool("path/to/your/file3.xlsx")  
#     print(f"✅ Detected {len(sub_functions)} sub-functions")  
# except Exception as e:  
#     print(f"❌ Error: {e}")
  
print("\n" + "="*70)  
print("TEST COMPLETE")  
print("="*70)