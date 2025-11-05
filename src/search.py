import os
import requests
import json
from dotenv import load_dotenv
from src.vectorstore import FaissVectorStore
import anthropic

load_dotenv()

class RAGSearch:
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "all-MiniLM-L6-v2", llm_model: str = "claude-sonnet-4-5-20250929", workspace_id: str = "ExternalResei8Dz"):
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)
        # Load or build vectorstore
        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")
        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            from src.data_loader import load_all_documents
            docs = load_all_documents("data")
            self.vectorstore.build_from_documents(docs)
        else:
            self.vectorstore.load()

        # Get Claude API key using TR's authentication
        payload = {"workspace_id": workspace_id}
        url = "https://aiplatform.gcs.int.thomsonreuters.com/v1/anthropic/token"
        resp = requests.post(url, headers=None, json=payload)
        credentials = json.loads(resp.content)

        if 'anthropic_api_key' not in credentials:
            raise ValueError(f"Failed to retrieve Anthropic API key: {credentials}")

        self.llm = anthropic.Anthropic(api_key=credentials["anthropic_api_key"])
        self.llm_model = llm_model
        print(f"[INFO] Claude LLM initialized: {llm_model}")

    def search_and_summarize(self, query: str, top_k: int = 5) -> str:
        results = self.vectorstore.query(query, top_k=top_k)
        texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]
        context = "\n\n".join(texts)
        if not context:
            return "No relevant documents found."
        prompt = f"""Summarize the following context for the query: '{query}'\n\nContext:\n{context}\n\nSummary:"""

        # Use Claude API
        message = self.llm.messages.create(
            model=self.llm_model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract text from response
        response_text = ""
        for textblock in message.content:
            if hasattr(textblock, 'text'):
                response_text += textblock.text

        return response_text

# Example usage
if __name__ == "__main__":
    rag_search = RAGSearch()
    query = "What are gap areas in TR's External Research offerings?"
    summary = rag_search.search_and_summarize(query, top_k=3)
    print("Summary:", summary)