# test_file_parser.py  
from utils.file_parser import FileParser  
import os
  
def test_file_parser():  
    """Test file parser with your uploaded files"""
      
    # Initialize parser  
    parser = FileParser()
      
    print("=" * 70)  
    print("TESTING FILE PARSER")  
    print("=" * 70)
      
    # Test 1: BU Intelligence Document  
    print("\n[TEST 1] Parsing BU Intelligence Document...")  
    try:  
        bu_intelligence = parser.parse_bu_intelligence("data/Business Units/Marketing/Stage 1/1b-MKTG-BU Intelligence.docx")  
        print(f"✅ SUCCESS: Parsed BU Intelligence")  
        print(f"   Sections found: {list(bu_intelligence.keys())}")  
        print(f"   Content length: {len(bu_intelligence['full_content'])} characters")  
    except Exception as e:  
        print(f"❌ FAILED: {e}")
      
    # Test 2: Enriched Use Cases Excel  
    print("\n[TEST 2] Parsing Enriched Use Cases...")  
    try:  
        enriched_use_cases = parser.parse_enriched_use_cases("data/Business Units/Marketing/Stage 2/2b-MKTG-Existing Use Cases Enriched.xlsx")  
        print(f"✅ SUCCESS: Parsed Enriched Use Cases")  
        print(f"   Total use cases: {len(enriched_use_cases)}")  
        print(f"   Columns: {list(enriched_use_cases.columns[:5])}...")  
    except Exception as e:  
        print(f"❌ FAILED: {e}")
      
    # Test 3: Role Activity Mapping Excel  
    print("\n[TEST 3] Parsing Role Activity Mapping Excel...")  
    try:  
        role_activity_mapping = parser.parse_role_activity_mapping("data/Business Units/Marketing/Input Files/MKTG_Role-Activity Mapping_20.08.2025.xlsx")  
        print(f"✅ SUCCESS: Parsed Role Activity Mapping")  
        print(f"   Total sub-functions: {len(role_activity_mapping)}")  
        print(f"   Sub-functions found: {list(role_activity_mapping.keys())}")  
    except Exception as e:  
        print(f"❌ FAILED: {e}")
      
    # Test 4: Extract Metadata for ONE Sub-Function  
    print("\n[TEST 4] Extracting Metadata for 'Demand Generation' Sub-Function...")  
    try:  
        if 'Demand Generation' in role_activity_mapping:  
            df_demand_gen = role_activity_mapping['Demand Generation']  
            metadata = parser.extract_sub_function_metadata(df_demand_gen, 'Demand Generation')  
            print(f"✅ SUCCESS: Extracted Demand Generation Metadata")  
            print(f"   Total activities: {metadata['total_activities']}")  
            print(f"   Sample activity: {metadata['activities'][0]['activity']}")  
            print(f"   Time spent: {metadata['activities'][0]['time_spent_pct']}%")  
        else:  
            print(f"⚠️  'Demand Generation' sheet not found")  
    except Exception as e:  
        print(f"❌ FAILED: {e}")
      
    print("\n" + "=" * 70)  
    print("TEST COMPLETE")  
    print("=" * 70)
  
if __name__ == "__main__":  
    test_file_parser()