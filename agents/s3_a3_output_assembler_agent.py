# agents/output_assembler_agent.py  
"""  
AGENT 3: OUTPUT ASSEMBLER AGENT  
Responsibilities:  
- Validate generated use cases (27-column schema, word count)  
- Export use cases to Excel with formatting  
- Generate downloadable file  
"""
  
from tools.validation_tools import (  
    validate_use_case_tool,  
    export_to_excel_tool  
)  
from typing import List, Dict
  
class OutputAssemblerAgent:  
    """Agent for validation and Excel export"""
      
    def __init__(self):  
        self.name = "Output Assembler Agent"  
        print(f"🤖 {self.name} initialized")
      
    def validate_and_export(  
        self,  
        use_cases: List[Dict],  
        total_sub_functions: int  
    ) -> str:  
        """  
        Validate all use cases and export to Excel
          
        Args:  
            use_cases: List of all generated use cases  
            total_sub_functions: Total number of sub-functions processed
          
        Returns:  
            Path to generated Excel file  
        """  
        print(f"\n{'='*70}")  
        print(f"🤖 {self.name} - VALIDATING & EXPORTING")  
        print(f"{'='*70}")  
        print(f"   Total use cases: {len(use_cases)}")
          
        try:  
            # Validate use cases  
            errors = []  
            for i, uc in enumerate(use_cases, 1):  
                validation = validate_use_case_tool(uc)  
                if not validation['valid']:  
                    errors.append(f"UC {i}: Missing columns: {validation['missing_columns']}")
              
            if errors:  
                print(f"   ⚠️  Validation warnings: {len(errors)} errors")  
                for error in errors[:5]:  
                    print(f"      - {error}")  
            else:  
                print(f"   ✅ Validation passed: All use cases valid")
              
            # Export to Excel  
            output_file = export_to_excel_tool(use_cases, total_sub_functions)
              
            print(f"   ✅ Exported to: {output_file}")  
            return output_file
              
        except Exception as e:  
            print(f"   ❌ Error during validation/export: {e}")  
            raise  