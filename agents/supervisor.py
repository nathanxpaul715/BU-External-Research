"""
Agentic RAG System using LangGraph
Implements a multi-agent RAG pipeline with query analysis, retrieval, and synthesis
"""
from typing import TypedDict, List, Annotated
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator


class AgentState(TypedDict):
    """State shared across the agent graph"""
    messages: Annotated[List[BaseMessage], operator.add]
    query: str
    refined_query: str
    retrieved_docs: List[str]
    final_answer: str
    next_action: str


class AgenticRAG:
    """Agentic RAG system with query refinement, retrieval, and synthesis"""

    def __init__(self, llm, retriever):
        """
        Initialize the agentic RAG system

        Args:
            llm: Language model (Claude from Anthropic)
            retriever: Vector store retriever
        """
        self.llm = llm
        self.retriever = retriever
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("query_analyzer", self.query_analyzer_node)
        workflow.add_node("retriever", self.retriever_node)
        workflow.add_node("relevance_checker", self.relevance_checker_node)
        workflow.add_node("synthesizer", self.synthesizer_node)

        # Define edges
        workflow.set_entry_point("query_analyzer")
        workflow.add_edge("query_analyzer", "retriever")
        workflow.add_edge("retriever", "relevance_checker")

        # Conditional edge based on relevance check
        workflow.add_conditional_edges(
            "relevance_checker",
            self.decide_next_step,
            {
                "synthesize": "synthesizer",
                "refine_query": "query_analyzer",
                "end": END
            }
        )

        workflow.add_edge("synthesizer", END)

        return workflow.compile()

    def query_analyzer_node(self, state: AgentState) -> AgentState:
        """
        Analyze and refine the user query for better retrieval
        """
        query = state.get("query", "")

        if not state.get("refined_query"):
            # First time analyzing
            analysis_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a query analysis expert. Your job is to refine user queries to make them more effective for document retrieval.

                Analyze the query and:
                1. Identify key concepts and entities
                2. Expand abbreviations if present
                3. Add relevant context keywords
                4. Make the query more specific and searchable

                Return ONLY the refined query, nothing else."""),
                ("human", "Original query: {query}")
            ])

            messages = analysis_prompt.format_messages(query=query)
            response = self.llm.invoke(messages)

            # Extract text from response
            if hasattr(response, 'content'):
                if isinstance(response.content, list):
                    refined_query = response.content[0].text if response.content else query
                else:
                    refined_query = response.content
            else:
                refined_query = query

            state["refined_query"] = refined_query
            state["messages"].append(HumanMessage(content=f"Refined query: {refined_query}"))

        return state

    def retriever_node(self, state: AgentState) -> AgentState:
        """
        Retrieve relevant documents using the refined query
        """
        refined_query = state.get("refined_query", state["query"])

        # Retrieve documents
        docs = self.retriever.get_relevant_documents(refined_query)

        # Store document contents
        retrieved_docs = [doc.page_content for doc in docs]
        state["retrieved_docs"] = retrieved_docs

        state["messages"].append(
            AIMessage(content=f"Retrieved {len(docs)} documents")
        )

        return state

    def relevance_checker_node(self, state: AgentState) -> AgentState:
        """
        Check if retrieved documents are relevant to the query
        """
        query = state["query"]
        docs = state.get("retrieved_docs", [])

        if not docs:
            state["next_action"] = "end"
            state["final_answer"] = "No relevant documents found."
            return state

        # Create context from retrieved docs
        context = "\n\n".join([f"Document {i+1}: {doc[:500]}..."
                               for i, doc in enumerate(docs[:3])])

        relevance_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a relevance evaluator. Determine if the retrieved documents contain information relevant to answering the user's query.

            Respond with ONLY one of these:
            - "RELEVANT" if documents can help answer the query
            - "IRRELEVANT" if documents don't contain useful information
            - "REFINE" if the query needs refinement for better results"""),
            ("human", "Query: {query}\n\nRetrieved Documents:\n{context}\n\nEvaluation:")
        ])

        messages = relevance_prompt.format_messages(query=query, context=context)
        response = self.llm.invoke(messages)

        # Extract evaluation
        if hasattr(response, 'content'):
            if isinstance(response.content, list):
                evaluation = response.content[0].text.strip().upper() if response.content else "RELEVANT"
            else:
                evaluation = response.content.strip().upper()
        else:
            evaluation = "RELEVANT"

        if "IRRELEVANT" in evaluation:
            state["next_action"] = "end"
            state["final_answer"] = "I couldn't find relevant information in the documents."
        elif "REFINE" in evaluation and not state.get("query_refined_count", 0):
            state["next_action"] = "refine_query"
            state["query_refined_count"] = state.get("query_refined_count", 0) + 1
        else:
            state["next_action"] = "synthesize"

        return state

    def synthesizer_node(self, state: AgentState) -> AgentState:
        """
        Synthesize final answer from retrieved documents
        """
        query = state["query"]
        docs = state.get("retrieved_docs", [])

        # Create comprehensive context
        context = "\n\n".join([f"Document {i+1}:\n{doc}"
                               for i, doc in enumerate(docs)])

        synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant. Use the provided documents to answer the user's question comprehensively and accurately.

            Guidelines:
            - Base your answer primarily on the provided documents
            - If information is not in the documents, say so
            - Cite specific documents when making claims
            - Be concise but thorough
            - If documents contain conflicting information, acknowledge it"""),
            ("human", "Question: {query}\n\nRetrieved Documents:\n{context}\n\nAnswer:")
        ])

        messages = synthesis_prompt.format_messages(query=query, context=context)
        response = self.llm.invoke(messages)

        # Extract answer
        if hasattr(response, 'content'):
            if isinstance(response.content, list):
                answer = response.content[0].text if response.content else "Unable to generate answer."
            else:
                answer = response.content
        else:
            answer = str(response)

        state["final_answer"] = answer
        state["messages"].append(AIMessage(content=answer))

        return state

    def decide_next_step(self, state: AgentState) -> str:
        """
        Routing function to decide next step based on relevance check
        """
        return state.get("next_action", "synthesize")

    def query(self, question: str) -> dict:
        """
        Execute the RAG pipeline for a user question

        Args:
            question: User's question

        Returns:
            Dictionary with final answer and execution state
        """
        initial_state = {
            "messages": [],
            "query": question,
            "refined_query": "",
            "retrieved_docs": [],
            "final_answer": "",
            "next_action": "",
        }

        final_state = self.graph.invoke(initial_state)

        return {
            "question": question,
            "answer": final_state.get("final_answer", ""),
            "refined_query": final_state.get("refined_query", ""),
            "num_docs_retrieved": len(final_state.get("retrieved_docs", [])),
        }

    def stream_query(self, question: str):
        """
        Stream the RAG pipeline execution for a user question

        Args:
            question: User's question

        Yields:
            State updates during execution
        """
        initial_state = {
            "messages": [],
            "query": question,
            "refined_query": "",
            "retrieved_docs": [],
            "final_answer": "",
            "next_action": "",
        }

        for state in self.graph.stream(initial_state):
            yield state
