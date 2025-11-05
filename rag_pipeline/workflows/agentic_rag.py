"""
Agentic RAG Workflow with LangGraph
Orchestrates the complete RAG pipeline with multi-stage retrieval
"""
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
import operator
from langgraph.graph import StateGraph, END

from ..config.settings import RAGPipelineConfig
from ..llm.claude_wrapper import ClaudeLLM
from ..embeddings.openai_embeddings import CachedOpenAIEmbeddings
from ..agents.rag_agents import MultiStageRetriever
from ..memory.job_memory import JobMemoryManager


class RAGState(TypedDict):
    """
    State for RAG workflow
    """
    # Input
    query: str
    original_query: str

    # Retrieval
    context: str
    chunks: List[Dict[str, Any]]
    sources: List[str]
    retrieval_time_ms: float

    # Generation
    answer: str
    refined_query: str

    # Metadata
    job_memory: str
    cost: float
    quality_score: float

    # Workflow control
    needs_refinement: bool
    iteration: int


class AgenticRAGWorkflow:
    """
    Agentic RAG Workflow using LangGraph
    Implements query refinement, retrieval, and generation with memory
    """

    def __init__(
        self,
        llm: ClaudeLLM,
        retriever: MultiStageRetriever,
        job_memory: Optional[JobMemoryManager] = None,
        config: Optional[RAGPipelineConfig] = None
    ):
        """
        Initialize agentic RAG workflow

        Args:
            llm: Claude LLM instance
            retriever: Multi-stage retriever
            job_memory: Optional job memory manager
            config: Pipeline configuration
        """
        self.llm = llm
        self.retriever = retriever
        self.job_memory = job_memory
        self.config = config or RAGPipelineConfig()

        # Build workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Build LangGraph workflow

        Returns:
            Compiled workflow graph
        """
        # Define workflow
        workflow = StateGraph(RAGState)

        # Add nodes
        workflow.add_node("refine_query", self._refine_query)
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("generate", self._generate)
        workflow.add_node("evaluate", self._evaluate)

        # Define edges
        workflow.set_entry_point("refine_query")
        workflow.add_edge("refine_query", "retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", "evaluate")

        # Conditional edge from evaluate
        workflow.add_conditional_edges(
            "evaluate",
            self._should_continue,
            {
                "continue": "refine_query",
                "end": END
            }
        )

        # Compile
        return workflow.compile()

    def _refine_query(self, state: RAGState) -> RAGState:
        """
        Node: Refine query for better retrieval
        """
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] NODE: Refine Query")

        query = state.get("query", state.get("original_query", ""))

        # On first iteration, analyze and potentially refine
        if state.get("iteration", 0) == 0:
            prompt = f"""Analyze this user query and refine it for semantic search if needed.
Focus on extracting key concepts and expanding abbreviations.

Original Query: {query}

Provide a refined query that will retrieve better results. If the query is already clear, return it as-is.
Output only the refined query, nothing else."""

            try:
                refined = self.llm.generate(prompt, max_tokens=200)
                refined = refined.strip()

                if refined and refined != query:
                    print(f"  Original: {query}")
                    print(f"  Refined:  {refined}")
                    state["refined_query"] = refined
                    state["query"] = refined
                else:
                    state["refined_query"] = query
            except Exception as e:
                print(f"  Error refining query: {e}")
                state["refined_query"] = query

        else:
            # Subsequent iterations - keep refined query
            state["query"] = state.get("refined_query", query)

        return state

    def _retrieve(self, state: RAGState) -> RAGState:
        """
        Node: Multi-stage retrieval
        """
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] NODE: Retrieve")

        query = state["query"]

        # Execute retrieval
        result = self.retriever.retrieve(query, use_hybrid=False)

        # Update state
        state["context"] = result["context"]
        state["chunks"] = result["chunks"]
        state["sources"] = result["sources"]
        state["retrieval_time_ms"] = result["retrieval_time_ms"]

        print(f"  Retrieved {result['num_chunks']} chunks from {len(result['sources'])} sources")

        return state

    def _generate(self, state: RAGState) -> RAGState:
        """
        Node: Generate answer using Claude
        """
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] NODE: Generate Answer")

        query = state["original_query"]
        context = state["context"]

        # Get job memory if available
        memory_context = ""
        if self.job_memory:
            memory_context = f"\n\nJob Context:\n{self.job_memory.get_compressed_memory()}\n"

        # Build system prompt
        system_prompt = """You are a highly knowledgeable AI assistant specializing in business intelligence and marketing analysis.

Your task is to answer questions based on the provided context documents. Follow these guidelines:

1. Answer based ONLY on the provided context
2. Be specific and cite sources when possible
3. If the context doesn't contain enough information, acknowledge this clearly
4. Provide actionable insights when relevant
5. Structure your answer clearly with sections if appropriate"""

        # Build user prompt
        user_prompt = f"""{memory_context}

Context Documents:
{context}

Question: {query}

Please provide a comprehensive answer based on the context provided."""

        # Generate answer
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = self.llm.invoke(messages, temperature=0.7)

            # Extract answer
            answer = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    answer += block.text

            state["answer"] = answer

            # Calculate cost (rough estimate)
            input_tokens = self.llm.count_tokens(user_prompt + system_prompt)
            output_tokens = self.llm.count_tokens(answer)
            cost = self.llm.calculate_cost(input_tokens, output_tokens)
            state["cost"] = state.get("cost", 0) + cost

            print(f"  Generated {output_tokens} tokens")
            print(f"  Cost: ${cost:.4f}")

        except Exception as e:
            print(f"  Error generating answer: {e}")
            state["answer"] = f"Error generating answer: {str(e)}"
            state["needs_refinement"] = False

        return state

    def _evaluate(self, state: RAGState) -> RAGState:
        """
        Node: Evaluate answer quality
        """
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] NODE: Evaluate")

        # Simple heuristic evaluation
        answer = state.get("answer", "")

        # Quality checks
        quality_score = 100

        # Check 1: Answer length (should be substantive)
        if len(answer) < 100:
            quality_score -= 20
            print("  Quality check: Answer too short (-20)")

        # Check 2: Contains "I don't know" or similar
        uncertain_phrases = ["i don't know", "not sure", "cannot determine", "unclear"]
        if any(phrase in answer.lower() for phrase in uncertain_phrases):
            quality_score -= 15
            print("  Quality check: Contains uncertainty (-15)")

        # Check 3: Has sources
        num_sources = len(state.get("sources", []))
        if num_sources == 0:
            quality_score -= 25
            print("  Quality check: No sources (-25)")
        elif num_sources < 2:
            quality_score -= 10
            print("  Quality check: Limited sources (-10)")

        # Check 4: Error in answer
        if "error" in answer.lower():
            quality_score -= 30
            print("  Quality check: Contains error (-30)")

        state["quality_score"] = max(0, quality_score)

        print(f"  Quality Score: {state['quality_score']:.1f}")

        # Update iteration
        state["iteration"] = state.get("iteration", 0) + 1

        # Decide if refinement needed (disabled for now - single pass)
        state["needs_refinement"] = False

        return state

    def _should_continue(self, state: RAGState) -> str:
        """
        Decide whether to continue iterating or end

        Args:
            state: Current state

        Returns:
            "continue" or "end"
        """
        # For now, single-pass only
        # Could add iteration logic based on quality score
        return "end"

    def query(self, query: str) -> Dict[str, Any]:
        """
        Execute RAG query

        Args:
            query: User query

        Returns:
            Result dictionary
        """
        print(f"\n{'='*70}")
        print(f"AGENTIC RAG WORKFLOW")
        print(f"Query: {query}")
        print(f"{'='*70}")

        start_time = datetime.now()

        # Initialize state
        initial_state = RAGState(
            query=query,
            original_query=query,
            context="",
            chunks=[],
            sources=[],
            retrieval_time_ms=0,
            answer="",
            refined_query=query,
            job_memory="",
            cost=0,
            quality_score=0,
            needs_refinement=False,
            iteration=0
        )

        # Run workflow
        final_state = self.workflow.invoke(initial_state)

        # Calculate total time
        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"\n{'='*70}")
        print(f"WORKFLOW COMPLETE")
        print(f"  Total time: {elapsed:.2f}s")
        print(f"  Quality score: {final_state['quality_score']:.1f}")
        print(f"  Total cost: ${final_state['cost']:.4f}")
        print(f"{'='*70}\n")

        # Return result
        return {
            "query": query,
            "refined_query": final_state["refined_query"],
            "answer": final_state["answer"],
            "context": final_state["context"],
            "chunks": final_state["chunks"],
            "sources": final_state["sources"],
            "quality_score": final_state["quality_score"],
            "cost": final_state["cost"],
            "retrieval_time_ms": final_state["retrieval_time_ms"],
            "total_time_s": elapsed,
            "num_chunks": len(final_state["chunks"])
        }


class SimpleRAGWorkflow:
    """
    Simplified RAG workflow without LangGraph for easier setup
    Provides the same functionality with direct function calls
    """

    def __init__(
        self,
        llm: ClaudeLLM,
        retriever: MultiStageRetriever,
        job_memory: Optional[JobMemoryManager] = None,
        config: Optional[RAGPipelineConfig] = None
    ):
        """
        Initialize simple RAG workflow

        Args:
            llm: Claude LLM instance
            retriever: Multi-stage retriever
            job_memory: Optional job memory manager
            config: Pipeline configuration
        """
        self.llm = llm
        self.retriever = retriever
        self.job_memory = job_memory
        self.config = config or RAGPipelineConfig()

    def query(self, query: str, refine_query: bool = True) -> Dict[str, Any]:
        """
        Execute RAG query

        Args:
            query: User query
            refine_query: Whether to refine the query first

        Returns:
            Result dictionary
        """
        print(f"\n{'='*70}")
        print(f"RAG WORKFLOW")
        print(f"Query: {query}")
        print(f"{'='*70}")

        start_time = datetime.now()
        total_cost = 0

        # Step 1: Refine query (optional)
        refined_query = query
        if refine_query:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Step 1: Refine Query")
            try:
                prompt = f"""Analyze this query and refine it for semantic search if needed.
Focus on key concepts and expand abbreviations.

Query: {query}

Provide a refined query. If already clear, return as-is. Output only the refined query."""

                refined_query = self.llm.generate(prompt, max_tokens=200).strip()
                if refined_query != query:
                    print(f"  Refined: {refined_query}")
                else:
                    print(f"  Query unchanged")

                # Estimate cost
                cost = self.llm.calculate_cost(
                    self.llm.count_tokens(prompt),
                    self.llm.count_tokens(refined_query)
                )
                total_cost += cost

            except Exception as e:
                print(f"  Error refining: {e}")
                refined_query = query

        # Step 2: Retrieve
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Step 2: Retrieve Context")
        retrieval_result = self.retriever.retrieve(refined_query)

        # Step 3: Generate
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Step 3: Generate Answer")

        # Get job memory if available
        memory_context = ""
        if self.job_memory:
            memory_context = f"\n\nJob Context:\n{self.job_memory.get_compressed_memory()}\n"

        # Generate answer
        system_prompt = """You are a highly knowledgeable AI assistant specializing in business intelligence and marketing analysis.

Answer questions based ONLY on the provided context. Be specific, cite sources, and provide actionable insights."""

        user_prompt = f"""{memory_context}

Context Documents:
{retrieval_result['context']}

Question: {query}

Please provide a comprehensive answer based on the context provided."""

        try:
            answer = self.llm.generate_with_context(
                query=query,
                context=retrieval_result['context'],
                system_prompt=system_prompt,
                temperature=0.7
            )

            # Calculate cost
            input_tokens = self.llm.count_tokens(user_prompt + system_prompt)
            output_tokens = self.llm.count_tokens(answer)
            cost = self.llm.calculate_cost(input_tokens, output_tokens)
            total_cost += cost

            print(f"  Generated {output_tokens} tokens")
            print(f"  Cost: ${cost:.4f}")

        except Exception as e:
            print(f"  Error generating: {e}")
            answer = f"Error: {str(e)}"

        # Calculate total time
        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"\n{'='*70}")
        print(f"WORKFLOW COMPLETE")
        print(f"  Total time: {elapsed:.2f}s")
        print(f"  Total cost: ${total_cost:.4f}")
        print(f"{'='*70}\n")

        return {
            "query": query,
            "refined_query": refined_query,
            "answer": answer,
            "context": retrieval_result['context'],
            "chunks": retrieval_result['chunks'],
            "sources": retrieval_result['sources'],
            "cost": total_cost,
            "retrieval_time_ms": retrieval_result['retrieval_time_ms'],
            "total_time_s": elapsed,
            "num_chunks": retrieval_result['num_chunks']
        }
