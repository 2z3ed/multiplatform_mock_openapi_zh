"""Model factory for AI layer."""

import os
from typing import Optional


def get_chat_model(
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    api_key: Optional[str] = None
) -> "MockChatModel":
    return MockChatModel(
        model_name=model_name or os.getenv("LLM_MODEL", "gpt-4"),
        temperature=temperature,
        api_key=api_key or os.getenv("OPENAI_API_KEY", "")
    )


class MockChatModel:
    def __init__(self, model_name: str, temperature: float, api_key: str):
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key

    def invoke(self, messages: list[dict]) -> str:
        return f"Mock response for: {messages[-1].get('content', '')}"

    def with_structured_output(self, schema: type):
        return MockStructuredOutput(schema)


class MockStructuredOutput:
    def __init__(self, schema: type):
        self.schema = schema

    def invoke(self, messages: list[dict]) -> dict:
        return {
            "intent": "faq",
            "confidence": 0.85,
        }