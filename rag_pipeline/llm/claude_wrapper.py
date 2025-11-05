"""
Claude LLM Wrapper for Thomson Reuters AI Platform
Handles authentication and message generation using Claude Sonnet 4
"""
import anthropic
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..config.settings import ClaudeConfig


class ClaudeLLM:
    """
    Wrapper for Claude API with Thomson Reuters authentication
    Compatible with LangChain-style invoke() interface
    """

    def __init__(self, config: Optional[ClaudeConfig] = None):
        """
        Initialize Claude LLM wrapper

        Args:
            config: Claude configuration (uses default if not provided)
        """
        self.config = config or ClaudeConfig()
        self.client = None
        self.api_key = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Thomson Reuters AI Platform"""
        payload = {
            "workspace_id": self.config.workspace_id,
        }

        try:
            resp = requests.post(
                self.config.token_url,
                headers=None,
                json=payload
            )
            credentials = json.loads(resp.content)

            if 'anthropic_api_key' in credentials:
                self.api_key = credentials["anthropic_api_key"]
                self.client = anthropic.Anthropic(api_key=self.api_key)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Claude client authenticated successfully")
            else:
                raise Exception(f"Failed to get API key: {credentials}")

        except Exception as e:
            raise Exception(f"Claude authentication failed: {str(e)}")

    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        """
        Invoke Claude API with messages (LangChain-compatible interface)

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Claude message response object
        """
        if not self.client:
            raise Exception("Claude client not authenticated. Call _authenticate() first.")

        # Extract system message if present
        system_message = None
        claude_messages = []

        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role")
                content = msg.get("content")
            else:
                # Handle LangChain message objects
                role = "user" if msg.__class__.__name__ == "HumanMessage" else "assistant"
                content = msg.content
                if msg.__class__.__name__ == "SystemMessage":
                    system_message = content
                    continue

            if role == "system":
                system_message = content
            else:
                claude_messages.append({
                    "role": role,
                    "content": content
                })

        # Ensure at least one message
        if not claude_messages:
            claude_messages.append({
                "role": "user",
                "content": "Hello"
            })

        # Prepare API call parameters
        api_params = {
            "model": kwargs.get("model", self.config.model),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "messages": claude_messages,
        }

        # Add system message if present
        if system_message:
            api_params["system"] = system_message

        # Add optional parameters
        if "temperature" in kwargs:
            api_params["temperature"] = kwargs["temperature"]
        elif self.config.temperature:
            api_params["temperature"] = self.config.temperature

        # Call Claude API
        try:
            response = self.client.messages.create(**api_params)
            return response
        except Exception as e:
            raise Exception(f"Claude API call failed: {str(e)}")

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Simple generation interface - returns text directly

        Args:
            prompt: User prompt
            **kwargs: Additional parameters

        Returns:
            Generated text string
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.invoke(messages, **kwargs)

        # Extract text from response
        text_content = ""
        for block in response.content:
            if hasattr(block, 'text'):
                text_content += block.text

        return text_content

    def generate_with_context(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate response with context (RAG pattern)

        Args:
            query: User query
            context: Retrieved context
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            Generated text string
        """
        # Build prompt with context
        user_message = f"""Context:
{context}

Question: {query}

Please answer the question based on the provided context. If the context doesn't contain enough information to answer the question, say so clearly."""

        messages = [{"role": "user", "content": user_message}]

        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})

        response = self.invoke(messages, **kwargs)

        # Extract text from response
        text_content = ""
        for block in response.content:
            if hasattr(block, 'text'):
                text_content += block.text

        return text_content

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate API call cost

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        # Claude Sonnet 4 pricing (as of 2025)
        # Input: $3 per million tokens
        # Output: $15 per million tokens
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        return input_cost + output_cost


class ClaudeStreamingLLM(ClaudeLLM):
    """Extended Claude LLM with streaming support"""

    def invoke_stream(self, messages: List[Dict[str, str]], **kwargs):
        """
        Invoke Claude API with streaming

        Args:
            messages: List of message dicts
            **kwargs: Additional parameters

        Yields:
            Text chunks as they arrive
        """
        if not self.client:
            raise Exception("Claude client not authenticated.")

        # Prepare messages same as invoke()
        system_message = None
        claude_messages = []

        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role")
                content = msg.get("content")
            else:
                role = "user" if msg.__class__.__name__ == "HumanMessage" else "assistant"
                content = msg.content
                if msg.__class__.__name__ == "SystemMessage":
                    system_message = content
                    continue

            if role == "system":
                system_message = content
            else:
                claude_messages.append({"role": role, "content": content})

        if not claude_messages:
            claude_messages.append({"role": "user", "content": "Hello"})

        # Prepare API call
        api_params = {
            "model": kwargs.get("model", self.config.model),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "messages": claude_messages,
        }

        if system_message:
            api_params["system"] = system_message

        # Stream response
        with self.client.messages.stream(**api_params) as stream:
            for text in stream.text_stream:
                yield text


# Convenience function
def get_claude_llm(config: Optional[ClaudeConfig] = None) -> ClaudeLLM:
    """
    Factory function to create Claude LLM instance

    Args:
        config: Optional Claude configuration

    Returns:
        Initialized ClaudeLLM instance
    """
    return ClaudeLLM(config)
