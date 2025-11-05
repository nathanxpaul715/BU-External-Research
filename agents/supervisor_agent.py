# agents/supervisor_agent.py  
"""  
SUPERVISOR AGENT (LangGraph)  
Responsibilities:  
- Orchestrate all 3 agents  
- Manage state transitions using LangGraph  
- Handle conditional routing  
- Track progress across all N sub-functions  
"""
  
from langgraph.graph import StateGraph, END  
from state_schema import AgentState  
from typing import Dict, Callable, Optional  
from agents.s3_a1_file_orchestrator_agent import FileOrchestratorAgent  
from agents.s3_a2_use_case_generator_agent import UseCaseGeneratorAgent  
from agents.s3_a3_output_assembler_agent import OutputAssemblerAgent
  
class SupervisorAgent:  
    """LangGraph supervisor that orchestrates all agents"""
      
    def __init__(self):  
        self.name = "Supervisor Agent (LangGraph)"
          
        print(f"\n{'='*70}")  
        print(f"🎯 {self.name} - INITIALIZING")  
        print(f"{'='*70}")
          
        self.file_orchestrator = FileOrchestratorAgent()  
        self.use_case_generator = UseCaseGeneratorAgent()  
        self.output_assembler = OutputAssemblerAgent()
          
        self.workflow = self._create_workflow()
          
        print(f"✅ {self.name} initialized with 3 agents")  
        print(f"{'='*70}")
      
    def _create_workflow(self) -> StateGraph:  
        """Create LangGraph state machine workflow"""
          
        workflow = StateGraph(AgentState)
          
        # Add nodes  
        workflow.add_node("parse_files", self._parse_files_node)  
        workflow.add_node("check_strategic_priorities", self._check_strategic_priorities_node)  
        workflow.add_node("process_sub_function", self._process_sub_function_node)  
        workflow.add_node("check_remaining", self._check_remaining_node)  
        workflow.add_node("validate_and_export", self._validate_and_export_node)
          
        # Define edges  
        workflow.set_entry_point("parse_files")  
        workflow.add_edge("parse_files", "check_strategic_priorities")  
        workflow.add_edge("check_strategic_priorities", "process_sub_function")  
        workflow.add_edge("process_sub_function", "check_remaining")
          
        # Conditional routing  
        workflow.add_conditional_edges(  
            "check_remaining",  
            self._route_next_action,  
            {  
                "continue": "process_sub_function",  
                "finalize": "validate_and_export"  
            }  
        )
          
        workflow.add_edge("validate_and_export", END)
          
        return workflow.compile()
      
    # Node functions  
    def _parse_files_node(self, state: AgentState) -> AgentState:  
        """Node: File Orchestrator Agent - Parse files"""  
        print(f"\n{'='*70}")  
        print(f"📋 NODE: Parse Files (Agent 1)")  
        print(f"{'='*70}")
          
        try:  
            parsed_data = self.file_orchestrator.parse_files(  
                file1_path=state['file1_path'],  
                file3_path=state['file3_path'],  
                data_folder_path=state['data_folder_path']  
            )
              
            state['sub_functions'] = parsed_data['sub_functions']  
            state['bu_intelligence'] = parsed_data['bu_context']  
            state['enriched_use_cases'] = parsed_data['existing_use_cases']  
            state['total_sub_functions'] = parsed_data['total_sub_functions']  
            state['current_sub_function_index'] = 0  
            state['uc_counter'] = 0  
            state['generated_use_cases'] = []  
            state['errors'] = []
              
            print(f"✅ State updated: {state['total_sub_functions']} sub-functions detected")
              
        except Exception as e:  
            state['errors'].append(f"File parsing error: {str(e)}")  
            print(f"❌ Error in parse_files_node: {e}")
          
        return state
      
    def _check_strategic_priorities_node(self, state: AgentState) -> AgentState:  
        """Node: Check if File 5+ uploaded"""  
        print(f"\n{'='*70}")  
        print(f"📋 NODE: Check Strategic Priorities")  
        print(f"{'='*70}")
          
        has_file5 = state.get('file5_path') is not None  
        state['has_strategic_priorities'] = has_file5
          
        if has_file5:  
            print(f"✅ Strategic priorities detected: {state['file5_path']}")  
        else:  
            print(f"ℹ️  No strategic priorities - using standard 6-tier prioritization")
          
        return state
      
    def _process_sub_function_node(self, state: AgentState) -> AgentState:  
        """Node: Process one sub-function"""
          
        current_index = state['current_sub_function_index']  
        sub_function_name = state['sub_functions'][current_index]
          
        print(f"\n{'='*70}")  
        print(f"📋 NODE: Process Sub-Function [{current_index + 1}/{state['total_sub_functions']}]")  
        print(f"📋 Sub-Function: {sub_function_name}")  
        print(f"{'='*70}")
          
        try:  
            # Extract activities  
            activities = self.file_orchestrator.extract_activities_for_sub_function(  
                file3_path=state['file3_path'],  
                sub_function_name=sub_function_name  
            )
              
            if not activities:  
                print(f"⚠️  No activities found, skipping...")  
                state['current_sub_function_index'] += 1  
                return state
              
            # Generate use cases  
            use_cases = self.use_case_generator.generate_use_cases(  
                sub_function_name=sub_function_name,  
                activities=activities,  
                bu_context=state['bu_intelligence'],  
                uc_counter=state['uc_counter']  
            )
              
            if use_cases:  
                state['generated_use_cases'].extend(use_cases)  
                state['uc_counter'] += len(use_cases)
                  
                print(f"✅ Completed '{sub_function_name}': {len(use_cases)} use cases")  
                print(f"📊 Total progress: {len(state['generated_use_cases'])}/{state['total_sub_functions'] * 8} use cases")  
            else:  
                print(f"⚠️  Failed to generate use cases")  
                state['errors'].append(f"Failed to generate use cases for {sub_function_name}")
              
            state['current_sub_function_index'] += 1
              
        except Exception as e:  
            state['errors'].append(f"Error processing {sub_function_name}: {str(e)}")  
            print(f"❌ Error: {e}")  
            state['current_sub_function_index'] += 1
          
        return state
      
    def _check_remaining_node(self, state: AgentState) -> AgentState:  
        """Node: Check if more sub-functions remain"""  
        remaining = state['total_sub_functions'] - state['current_sub_function_index']
          
        if remaining > 0:  
            print(f"\n📊 Remaining sub-functions: {remaining}")  
            state['processing_complete'] = False  
        else:  
            print(f"\n✅ All {state['total_sub_functions']} sub-functions processed")  
            state['processing_complete'] = True
          
        return state
      
    def _validate_and_export_node(self, state: AgentState) -> AgentState:  
        """Node: Validate and export"""  
        print(f"\n{'='*70}")  
        print(f"📋 NODE: Validate and Export (Agent 3)")  
        print(f"{'='*70}")
          
        try:  
            output_file = self.output_assembler.validate_and_export(  
                use_cases=state['generated_use_cases'],  
                total_sub_functions=state['total_sub_functions']  
            )
              
            state['output_file_path'] = output_file
              
            print(f"\n{'='*70}")  
            print(f"🎉 SUCCESS: {output_file}")  
            print(f"{'='*70}")
              
        except Exception as e:  
            state['errors'].append(f"Export error: {str(e)}")  
            print(f"❌ Error: {e}")
          
        return state
      
    def _route_next_action(self, state: AgentState) -> str:  
        """Conditional routing"""  
        if state['processing_complete']:  
            return "finalize"  
        else:  
            return "continue"
      
    def run(  
        self,  
        file1_path: str,  
        file3_path: str,  
        data_folder_path: str = "data/Business Units/Marketing/Stage 2",  
        file5_path: Optional[str] = None,  
        progress_callback: Optional[Callable] = None  
    ) -> str:  
        """Run the complete workflow"""  
        print(f"\n{'='*70}")  
        print(f"🎯 {self.name} - STARTING WORKFLOW")  
        print(f"{'='*70}")
          
        initial_state = {  
            'file1_path': file1_path,  
            'file3_path': file3_path,  
            'file5_path': file5_path,  
            'data_folder_path': data_folder_path,  
            'bu_intelligence': '',  
            'enriched_use_cases': [],  
            'sub_functions': [],  
            'total_sub_functions': 0,  
            'strategic_priorities': None,  
            'current_sub_function': None,  
            'current_sub_function_index': 0,  
            'current_activities': [],  
            'uc_counter': 0,  
            'generated_use_cases': [],  
            'has_strategic_priorities': False,  
            'processing_complete': False,  
            'validation_report': None,  
            'output_file_path': None,  
            'messages': [],  
            'errors': []  
        }
          
        for state in self.workflow.stream(initial_state):  
            if progress_callback and 'current_sub_function_index' in state and 'total_sub_functions' in state:  
                current = state['current_sub_function_index']  
                total = state['total_sub_functions']  
                if total > 0 and current > 0:  
                    sub_function = state['sub_functions'][min(current - 1, len(state['sub_functions']) - 1)]  
                    progress_callback(current, total, sub_function)
          
        final_state = state
          
        if final_state.get('errors'):  
            print(f"\n⚠️  Workflow completed with {len(final_state['errors'])} errors:")  
            for error in final_state['errors']:  
                print(f"   - {error}")
          
        return final_state.get('output_file_path')  