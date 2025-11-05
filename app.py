<<<<<<< HEAD
from src.data_loader import load_all_documents
from src.vectorstore import FaissVectorStore
from src.search import RAGSearch

# Example usage
if __name__ == "__main__":
    
    # docs = load_all_documents("data")
    store = FaissVectorStore("faiss_store")
    # store.build_from_documents(docs)
    store.load()
    # print(store.query("What is Public Speaking?", top_k=3))
    rag_search = RAGSearch()
    query = "What does Marketting BU Segment do in TR?"
    summary = rag_search.search_and_summarize(query, top_k=3)
    print("Summary:", summary)
=======
# app.py  
"""  
Streamlit UI for LangGraph Multi-Agent Use Case Generator  
Includes file upload, progress tracking, and download functionality  
"""
  
import streamlit as st  
import os  
from orchestrator_langgraph import run_langgraph_workflow
  
st.set_page_config(  
    page_title="AI Use Case Generator - LangGraph Multi-Agent",  
    page_icon="🚀",  
    layout="wide"  
)
  
# Initialize session state  
if 'processing_complete' not in st.session_state:  
    st.session_state.processing_complete = False  
if 'output_file' not in st.session_state:  
    st.session_state.output_file = None
  
# Title  
st.title("🚀 AI Use Case Generator")  
st.markdown("**LangGraph Multi-Agent Architecture with LangChain Tools**")  
st.markdown("*Autonomous generation of 8 use cases per sub-function with 27-column enrichment*")
  
st.divider()
  
# Instructions  
with st.expander("📋 How to Use", expanded=False):  
    st.markdown("""  
    **Step-by-step guide:**
      
    1. **Prepare Data Folder**: Ensure `data/` folder contains Enriched Use Cases Excel file  
    2. **Upload File 1**: BU Intelligence Document (Word format)  
    3. **Upload File 3**: Role Activity Mapping Excel (with all sub-function sheets)  
    4. **Optional**: Upload File 5+ (Strategic Priorities documents)  
    5. **Click Generate**: System will autonomously process all sub-functions  
    6. **Download**: Once complete, download the generated Excel file
      
    **What the system does:**  
    - **Agent 1 (File Orchestrator)**: Parses files, detects N sub-functions, extracts activities  
    - **Agent 2 (Use Case Generator)**: Generates 8 use cases per sub-function with Claude Sonnet 4.5  
    - **Agent 3 (Output Assembler)**: Validates and exports to Excel  
    - **Supervisor (LangGraph)**: Orchestrates all agents with state management
      
    **Note:** Use case IDs always start from UC-[ABBREV]-001 (no continuation from previous runs)  
    """)
  
st.divider()
  
# Data folder status check  
st.header("📂 Data Folder Status")  
data_folder = "data/Business Units/Marketing/Stage 2"
  
col_status1, col_status2 = st.columns([2, 1])
  
with col_status1:  
    if os.path.exists(data_folder):  
        files = os.listdir(data_folder)  
        excel_files = [f for f in files if f.endswith('.xlsx')]
          
        if excel_files:  
            st.success(f"✅ Data folder found with {len(excel_files)} Excel file(s)")
              
            # Check for Enriched Use Cases file  
            enriched_files = [f for f in excel_files if 'enriched' in f.lower() or 'use case' in f.lower()]  
            if enriched_files:  
                st.info(f"📋 Enriched Use Cases: `{enriched_files[0]}`")  
            else:  
                st.warning("⚠️ No Enriched Use Cases file found. Looking for files with 'enriched' or 'use case' in name.")  
        else:  
            st.error(f"❌ Data folder exists but no Excel files found")  
    else:  
        st.error(f"❌ Data folder not found")  
        st.code(f"# Create data folder and add Enriched Use Cases file:\nmkdir {data_folder}\ncp '2b-MKTG-Existing Use Cases Enriched.xlsx' {data_folder}/", language="bash")
  
with col_status2:  
    if os.path.exists(data_folder):  
        st.metric("Status", "✅ Ready", delta="Folder exists")  
    else:  
        st.metric("Status", "❌ Missing", delta="Create folder")
  
st.divider()
  
# File upload section  
st.header("📁 File Upload")
  
col1, col2 = st.columns(2)
  
with col1:  
    st.subheader("Required Files")
      
    # File 1: BU Intelligence  
    file1 = st.file_uploader(  
        "**File 1: BU Intelligence Document**",  
        type=['docx'],  
        key='file1',  
        help="Business context, strategy, competitors, vendors, tech stack"  
    )  
    if file1:  
        st.success(f"✅ {file1.name} ({file1.size / 1024:.1f} KB)")
      
    # File 3: Role Activity Mapping  
    file3 = st.file_uploader(  
        "**File 3: Role Activity Mapping Excel**",  
        type=['xlsx'],  
        key='file3',  
        help="Raw Excel with all sub-function sheets (excludes 'Summary' sheet)"  
    )  
    if file3:  
        st.success(f"✅ {file3.name} ({file3.size / 1024:.1f} KB)")
  
with col2:  
    st.subheader("Optional Files")
      
    # File 5+: Strategic Priorities  
    enable_file5 = st.checkbox(  
        "I have strategic priority documents to upload",  
        key='enable_file5',  
        help="Upload leadership priorities, strategy docs, OKRs for priority tier boosting"  
    )
      
    if enable_file5:  
        file5_list = st.file_uploader(  
            "**File 5+: Strategic Priority Documents**",  
            type=['docx', 'pdf'],  
            key='file5',  
            accept_multiple_files=True,  
            help="Marketing strategy PDFs, leadership priorities, initiative roadmaps, quarterly OKRs"  
        )  
        if file5_list:  
            st.success(f"✅ {len(file5_list)} document(s) uploaded:")  
            for f in file5_list:  
                st.text(f"  • {f.name} ({f.size / 1024:.1f} KB)")  
    else:  
        st.info("ℹ️ No strategic priorities - standard 6-tier prioritization will be used")  
        file5_list = None
  
st.divider()
  
# Processing section  
st.header("🚀 Processing")
  
# Check mandatory files  
mandatory_files_ready = file1 is not None and file3 is not None
  
if mandatory_files_ready:  
    st.success("✅ All required files ready for processing!")
      
    # Processing button  
    if st.button("🚀 **Generate Use Cases (LangGraph Multi-Agent)**", type="primary", use_container_width=True, disabled=st.session_state.processing_complete):
          
        # Reset state  
        st.session_state.processing_complete = False  
        st.session_state.output_file = None
          
        # Save uploaded files temporarily  
        temp_file1 = "temp_file1.docx"  
        temp_file3 = "temp_file3.xlsx"
          
        with open(temp_file1, "wb") as f:  
            f.write(file1.read())  
        with open(temp_file3, "wb") as f:  
            f.write(file3.read())
          
        # Save File 5+ if uploaded  
        file5_paths = []  
        if enable_file5 and file5_list:  
            for i, f5 in enumerate(file5_list):  
                f5_path = f"temp_file5_{i}.docx"  
                with open(f5_path, "wb") as f:  
                    f.write(f5.read())  
                file5_paths.append(f5_path)
          
        # Processing UI  
        st.markdown("---")  
        st.subheader("🔄 LangGraph Multi-Agent Processing")
          
        # Progress tracking  
        progress_container = st.container()
          
        with progress_container:  
            progress_bar = st.progress(0, text="Initializing...")  
            status_text = st.empty()  
            agent_status = st.empty()
          
        # Progress callback  
        def update_progress(current, total, sub_function):  
            progress = current / total  
            progress_bar.progress(  
                progress,   
                text=f"Processing {current} of {total} sub-functions ({progress*100:.0f}%)"  
            )  
            status_text.markdown(f"**Current Sub-Function:** {sub_function}")  
            agent_status.info(f"🤖 Agent 2 (Use Case Generator) working on '{sub_function}'...")
          
        # Run LangGraph workflow  
        with st.spinner("🤖 Initializing LangGraph Multi-Agent System..."):  
            try:  
                # Import and run orchestrator  
                output_file = run_langgraph_workflow(  
                    file1_path=temp_file1,  
                    file3_path=temp_file3,  
                    file5_paths=file5_paths if file5_paths else None,  
                    data_folder_path=data_folder,  
                    progress_callback=update_progress  
                )
                  
                if output_file and os.path.exists(output_file):  
                    # Update progress to complete  
                    progress_bar.progress(1.0, text="Processing Complete! ✅")  
                    status_text.markdown("**✅ All sub-functions processed successfully!**")  
                    agent_status.success("🎉 Agent 3 (Output Assembler) completed validation and export!")
                      
                    # Store output file in session state  
                    st.session_state.processing_complete = True  
                    st.session_state.output_file = output_file
                      
                    # Success message  
                    st.success("🎉 Use cases generated successfully!")
                      
                    # Display output info  
                    st.info(f"📊 **Output File:** `{output_file}`")
                      
                    # File size  
                    file_size = os.path.getsize(output_file) / 1024  
                    st.metric("File Size", f"{file_size:.1f} KB")
                      
                else:  
                    st.error("❌ Failed to generate use cases. Check console logs for errors.")
                      
            except Exception as e:  
                st.error(f"❌ Error during processing: {str(e)}")  
                st.exception(e)
              
            finally:  
                # Cleanup temp files  
                temp_files = [temp_file1, temp_file3] + file5_paths  
                for temp_file in temp_files:  
                    if temp_file and os.path.exists(temp_file):  
                        try:  
                            os.remove(temp_file)  
                        except:  
                            pass
      
    # Download section (shows after processing complete)  
    if st.session_state.processing_complete and st.session_state.output_file:  
        st.markdown("---")  
        st.subheader("📥 Download Generated Use Cases")
          
        output_file = st.session_state.output_file
          
        # Read file for download  
        with open(output_file, "rb") as f:  
            file_data = f.read()
          
        col_download1, col_download2 = st.columns([3, 1])
          
        with col_download1:  
            st.download_button(  
                label="📥 **Download Use Cases Excel File**",  
                data=file_data,  
                file_name=output_file,  
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  
                use_container_width=True,  
                type="primary"  
            )
          
        with col_download2:  
            if st.button("🔄 Reset", use_container_width=True):  
                st.session_state.processing_complete = False  
                st.session_state.output_file = None  
                st.rerun()
          
        # Display file details  
        st.markdown("**File Details:**")  
        file_size = os.path.getsize(output_file) / 1024  
        st.text(f"• File Name: {output_file}")  
        st.text(f"• File Size: {file_size:.1f} KB")  
        st.text(f"• Format: Excel (.xlsx)")  
        st.text(f"• Sheets: Use Cases (N×8 rows, 27 columns)")
  
else:  
    st.warning("⚠️ Please upload all required files to proceed")
      
    missing = []  
    if not file1:  
        missing.append("**File 1** (BU Intelligence Document)")  
    if not file3:  
        missing.append("**File 3** (Role Activity Mapping Excel)")
      
    if missing:  
        st.error(f"**Missing:** {', '.join(missing)}")  
        st.info("👆 Upload the missing files above to enable processing")
  
st.divider()
  
# System information  
st.header("ℹ️ System Information")
  
col_info1, col_info2, col_info3 = st.columns(3)
  
with col_info1:  
    st.metric("Architecture", "LangGraph", delta="Multi-Agent")  
    st.metric("Agents", "3 + 1 Supervisor")
  
with col_info2:  
    st.metric("LLM Model", "Claude Sonnet 4.5")  
    st.metric("Authentication", "Thomson Reuters")
  
with col_info3:  
    st.metric("Use Cases/Sub-Function", "8")  
    st.metric("Columns/Use Case", "27")
  
st.divider()
  
# Footer  
st.markdown("---")  
st.markdown("""  
<div style='text-align: center; color: #666;'>  
    <p><strong>🤖 LangGraph Multi-Agent Architecture</strong></p>  
    <p>Agent 1: File Orchestrator | Agent 2: Use Case Generator | Agent 3: Output Assembler | Supervisor: LangGraph</p>  
    <p>Powered by Claude Sonnet 4.5 | LangChain Tools | Thomson Reuters Authentication</p>  
    <p><em>File 2 (Enriched Use Cases) auto-loaded from data/ folder | Use Case IDs start from UC-001</em></p>  
</div>  
""", unsafe_allow_html=True)
>>>>>>> krishna_work
