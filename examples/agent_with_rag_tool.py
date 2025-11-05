"""
Example: How to integrate the RAG tool with different agent frameworks

This file demonstrates how to use the RAG tool with:
1. Anthropic Claude API (direct function calling)
2. LangChain agents
3. Custom agent implementations
"""

import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.rag_tool import (
    search_tr_knowledge_base,
    get_rag_tool,
    ANTHROPIC_TOOL_DEFINITION
)


# ==============================================================================
# Example 1: Using RAG Tool with Anthropic Claude API (Function Calling)
# ==============================================================================

def example_anthropic_agent():
    """
    Example of an agent using Claude with the RAG tool through function calling.
    """
    import anthropic
    import requests

    print("\n" + "=" * 80)
    print("Example 1: Anthropic Claude Agent with RAG Tool")
    print("=" * 80)

    # Get Claude API key using TR's authentication
    payload = {"workspace_id": "ExternalResei8Dz"}
    url = "https://aiplatform.gcs.int.thomsonreuters.com/v1/anthropic/token"
    resp = requests.post(url, headers=None, json=payload)
    credentials = json.loads(resp.content)

    if 'anthropic_api_key' not in credentials:
        print(f"Failed to get API key: {credentials}")
        return

    client = anthropic.Anthropic(api_key=credentials["anthropic_api_key"])

    # User query
    user_query = "What are the main gap areas in Thomson Reuters External Research offerings?"

    print(f"\nUser Query: {user_query}")
    print("\nAgent is thinking...\n")

    # First message: Agent decides to use the RAG tool
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        tools=[ANTHROPIC_TOOL_DEFINITION],
        messages=[
            {
                "role": "user",
                "content": user_query
            }
        ]
    )

    # Check if agent wants to use the tool
    if message.stop_reason == "tool_use":
        # Extract tool use from response
        tool_use = None
        for content_block in message.content:
            if content_block.type == "tool_use":
                tool_use = content_block
                break

        if tool_use and tool_use.name == "search_tr_knowledge_base":
            print(f"[Agent] Calling RAG tool with query: {tool_use.input['query']}")

            # Execute the tool
            tool_result = search_tr_knowledge_base(
                query=tool_use.input['query'],
                top_k=tool_use.input.get('top_k', 5),
                summarize=tool_use.input.get('summarize', True)
            )

            print(f"[Tool] Retrieved relevant information from knowledge base")
            print(f"[Tool Result Preview]: {tool_result[:200]}...\n")

            # Send tool result back to Claude
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                tools=[ANTHROPIC_TOOL_DEFINITION],
                messages=[
                    {"role": "user", "content": user_query},
                    {"role": "assistant", "content": message.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": tool_result
                            }
                        ]
                    }
                ]
            )

            # Extract final answer
            final_answer = ""
            for content_block in response.content:
                if hasattr(content_block, 'text'):
                    final_answer += content_block.text

            print("[Agent Final Response]:")
            print(final_answer)
    else:
        # Agent responded directly without using tool
        response_text = ""
        for content_block in message.content:
            if hasattr(content_block, 'text'):
                response_text += content_block.text
        print("[Agent Response]:")
        print(response_text)


# ==============================================================================
# Example 2: Simple Direct Usage (No Agent Framework)
# ==============================================================================

def example_simple_usage():
    """
    Simple direct usage of the RAG tool without any agent framework.
    """
    print("\n" + "=" * 80)
    print("Example 2: Simple Direct Usage")
    print("=" * 80)

    queries = [
        "What are TR's current research capabilities?",
        "What are the strategic initiatives for External Research?",
        "What gaps exist in TR's research offerings?"
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        result = search_tr_knowledge_base(query, top_k=3)
        print(f"Answer: {result[:300]}...\n")
        print("-" * 80)


# ==============================================================================
# Example 3: Using with LangChain Agents
# ==============================================================================

def example_langchain_agent():
    """
    Example of using the RAG tool with LangChain agents.
    """
    print("\n" + "=" * 80)
    print("Example 3: LangChain Agent with RAG Tool")
    print("=" * 80)

    try:
        from langchain.agents import AgentExecutor, create_tool_calling_agent
        from langchain_anthropic import ChatAnthropic
        from langchain.tools import Tool
        from langchain_core.prompts import ChatPromptTemplate
        from src.rag_tool import get_langchain_tool
        import requests

        # Get Claude API key
        payload = {"workspace_id": "ExternalResei8Dz"}
        url = "https://aiplatform.gcs.int.thomsonreuters.com/v1/anthropic/token"
        resp = requests.post(url, headers=None, json=payload)
        credentials = json.loads(resp.content)

        if 'anthropic_api_key' not in credentials:
            print(f"Failed to get API key: {credentials}")
            return

        # Create LangChain LLM
        llm = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
            anthropic_api_key=credentials["anthropic_api_key"]
        )

        # Get RAG tool
        rag_tool = get_langchain_tool()

        # Create additional tools if needed
        tools = [rag_tool] if rag_tool else []

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant with access to Thomson Reuters External Research knowledge base. Use the search_tr_knowledge_base tool to answer questions accurately."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        # Create agent
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        # Run the agent
        user_query = "What are the key findings about TR's research gap areas?"
        print(f"\nUser Query: {user_query}\n")

        result = agent_executor.invoke({"input": user_query})
        print(f"\n[Agent Response]:")
        print(result["output"])

    except ImportError as e:
        print(f"[WARNING] LangChain not fully installed: {e}")
        print("Install with: pip install langchain langchain-anthropic")
    except Exception as e:
        print(f"[ERROR] {e}")


# ==============================================================================
# Example 4: Custom Agent with RAG Tool
# ==============================================================================

class CustomAgentWithRAG:
    """
    Example of a custom agent implementation that uses the RAG tool.
    """

    def __init__(self):
        self.rag_tool = get_rag_tool()
        print("[Agent] Initialized with RAG tool access")

    def process_query(self, query: str) -> str:
        """
        Process a user query by:
        1. Determining if RAG search is needed
        2. Retrieving relevant context
        3. Formulating a response
        """
        print(f"\n[Agent] Processing query: {query}")

        # Simple keyword-based decision (in real scenarios, use LLM for this)
        research_keywords = ['gap', 'research', 'capability', 'TR', 'Thomson Reuters', 'External Research']
        needs_rag = any(keyword.lower() in query.lower() for keyword in research_keywords)

        if needs_rag:
            print("[Agent] Query requires knowledge base search")
            # Get context from RAG
            context_chunks = self.rag_tool.get_relevant_context(query, top_k=3)

            if context_chunks:
                print(f"[Agent] Retrieved {len(context_chunks)} relevant chunks")
                # Combine context
                context = "\n\n".join([chunk['text'] for chunk in context_chunks])
                response = f"Based on the TR External Research knowledge base:\n\n{context[:500]}..."
                return response
            else:
                return "I couldn't find relevant information in the knowledge base."
        else:
            return "This query doesn't seem to be about TR External Research. Please ask about research capabilities, gaps, or initiatives."

    def conversational_search(self, queries: list):
        """
        Handle multiple queries in a conversational manner.
        """
        print("\n" + "=" * 80)
        print("Example 4: Custom Agent with Conversational RAG")
        print("=" * 80)

        for i, query in enumerate(queries, 1):
            print(f"\n--- Turn {i} ---")
            response = self.process_query(query)
            print(f"[Agent Response]: {response[:300]}...")


# ==============================================================================
# Main Execution
# ==============================================================================

if __name__ == "__main__":
    print("TR External Research RAG Tool - Agent Integration Examples")
    print("=" * 80)

    # Choose which example to run
    print("\nSelect example to run:")
    print("1. Anthropic Claude Agent with Function Calling")
    print("2. Simple Direct Usage")
    print("3. LangChain Agent")
    print("4. Custom Agent Implementation")
    print("5. Run All Examples")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == "1":
        example_anthropic_agent()
    elif choice == "2":
        example_simple_usage()
    elif choice == "3":
        example_langchain_agent()
    elif choice == "4":
        agent = CustomAgentWithRAG()
        queries = [
            "What are the gap areas in TR research?",
            "Tell me about TR's research capabilities",
            "What's the weather today?"  # Should not trigger RAG
        ]
        agent.conversational_search(queries)
    elif choice == "5":
        example_simple_usage()
        example_anthropic_agent()
        agent = CustomAgentWithRAG()
        agent.conversational_search([
            "What are strategic initiatives?",
            "What capabilities does TR have?"
        ])
        # example_langchain_agent()  # Uncomment if langchain is installed
    else:
        print("Invalid choice. Running simple example...")
        example_simple_usage()
