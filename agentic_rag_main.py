"""
Agentic RAG Main Script
Complete implementation with document loading, vector store, and LangGraph RAG
"""
import anthropic
import requests
import json
import sys
import os
from pathlib import Path

# Add utils and agents to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from utils.document_loader import MultiFormatDocumentLoader
from utils.vector_store import VectorStoreManager
from agents.supervisor import AgenticRAG


class ClaudeRAGSystem:
    """Complete RAG system with Claude integration"""

    def __init__(self, data_path: str):
        """
        Initialize the RAG system

        Args:
            data_path: Path to directory containing input documents
        """
        self.data_path = data_path
        self.llm = None
        self.vector_store_manager = None
        self.rag_agent = None

    def setup_claude_client(self):
        """Set up Claude API client using workspace credentials"""
        print("Setting up Claude API client...")

        payload = {
            "workspace_id": "ExternalResei8Dz",
        }

        url = "https://aiplatform.gcs.int.thomsonreuters.com/v1/anthropic/token"

        # Send a POST request to get API key
        resp = requests.post(url, headers=None, json=payload)
        credentials = json.loads(resp.content)

        if 'anthropic_api_key' in credentials:
            self.llm = anthropic.Anthropic(
                api_key=credentials["anthropic_api_key"],
            )
            print("Claude client initialized successfully")
        else:
            raise Exception(f"Failed to get API key: {credentials}")

    def load_documents(self):
        """Load all documents from the data path"""
        print(f"\nLoading documents from: {self.data_path}")

        # Initialize document loader
        doc_loader = MultiFormatDocumentLoader(
            chunk_size=1000,
            chunk_overlap=200
        )

        # Check if path is directory or file
        data_path_obj = Path(self.data_path)

        if data_path_obj.is_dir():
            documents = doc_loader.load_directory(self.data_path)
        else:
            documents = doc_loader.load_document(self.data_path)

        # Get and print stats
        stats = doc_loader.get_document_stats(documents)
        print(f"\nDocument Loading Stats:")
        print(f"  Total chunks: {stats['total_documents']}")
        print(f"  Total characters: {stats['total_characters']}")
        print(f"  Average chunk size: {stats['avg_chunk_size']}")

        return documents

    def setup_vector_store(self, documents):
        """Create or load vector store"""
        print("\nSetting up vector store...")

        vector_store_path = os.path.join(
            os.path.dirname(__file__),
            "vector_store"
        )

        self.vector_store_manager = VectorStoreManager(
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            persist_directory=vector_store_path
        )

        # Try to load existing vector store, otherwise create new one
        if os.path.exists(vector_store_path):
            try:
                print("Loading existing vector store...")
                self.vector_store_manager.load_vector_store()
            except Exception as e:
                print(f"Could not load existing store: {e}")
                print("Creating new vector store...")
                self.vector_store_manager.create_vector_store(documents)
        else:
            print("Creating new vector store...")
            self.vector_store_manager.create_vector_store(documents)

        print("Vector store ready")

    def create_claude_llm_wrapper(self):
        """Create a wrapper for Claude that works with LangChain"""
        class ClaudeLLM:
            def __init__(self, client):
                self.client = client

            def invoke(self, messages):
                """Invoke Claude API with messages"""
                # Convert messages to Claude format
                claude_messages = []
                for msg in messages:
                    if hasattr(msg, 'content'):
                        role = "user" if msg.__class__.__name__ == "HumanMessage" else "assistant"
                        if msg.__class__.__name__ == "SystemMessage":
                            continue  # We'll handle system messages separately
                        claude_messages.append({
                            "role": role,
                            "content": msg.content
                        })

                # If no messages or only system messages, add default
                if not claude_messages:
                    claude_messages.append({
                        "role": "user",
                        "content": str(messages[0].content) if messages else "Hello"
                    })

                # Call Claude API
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    messages=claude_messages
                )

                return response

        return ClaudeLLM(self.llm)

    def initialize_rag_agent(self):
        """Initialize the LangGraph RAG agent"""
        print("\nInitializing Agentic RAG system...")

        # Create Claude LLM wrapper
        llm_wrapper = self.create_claude_llm_wrapper()

        # Get retriever from vector store
        retriever = self.vector_store_manager.get_retriever(k=5)

        # Initialize RAG agent
        self.rag_agent = AgenticRAG(
            llm=llm_wrapper,
            retriever=retriever
        )

        print("Agentic RAG system ready")

    def query(self, question: str):
        """
        Query the RAG system

        Args:
            question: User's question

        Returns:
            Response dictionary
        """
        if not self.rag_agent:
            raise Exception("RAG agent not initialized. Call initialize() first.")

        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}")

        result = self.rag_agent.query(question)

        print(f"\nRefined Query: {result['refined_query']}")
        print(f"Documents Retrieved: {result['num_docs_retrieved']}")
        print(f"\n{'-'*60}")
        print(f"Answer:\n{result['answer']}")
        print(f"{'-'*60}\n")

        return result

    def initialize(self):
        """Complete initialization of the RAG system"""
        # Step 1: Setup Claude
        self.setup_claude_client()

        # Step 2: Load documents
        documents = self.load_documents()

        if not documents:
            raise Exception("No documents loaded. Check your data path.")

        # Step 3: Setup vector store
        self.setup_vector_store(documents)

        # Step 4: Initialize RAG agent
        self.initialize_rag_agent()

        print("\n" + "="*60)
        print("RAG SYSTEM READY")
        print("="*60 + "\n")


def main():
    """Main execution function"""

    # Path to your data
    DATA_PATH = r"C:\Users\6122504\Documents\BU External Research\BU-External-Research\data\Prompts, Templates & Inputs"

    # Initialize RAG system
    rag_system = ClaudeRAGSystem(data_path=DATA_PATH)

    try:
        # Initialize all components
        rag_system.initialize()

        # Example queries
        example_queries = [
            "What are the main topics covered in the documents?",
            "Summarize the key information from the monthly updates",
            "What use cases are mentioned in the documents?",
        ]

        print("Running example queries...\n")

        for query in example_queries:
            result = rag_system.query(query)

        # Interactive mode
        print("\n" + "="*60)
        print("INTERACTIVE MODE - Enter your questions (or 'quit' to exit)")
        print("="*60 + "\n")

        while True:
            user_query = input("\nYour question: ").strip()

            if user_query.lower() in ['quit', 'exit', 'q']:
                print("Exiting...")
                break

            if not user_query:
                continue

            try:
                rag_system.query(user_query)
            except Exception as e:
                print(f"Error processing query: {str(e)}")

    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
