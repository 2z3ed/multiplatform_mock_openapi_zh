"""Model factory for AI layer."""

import os
from typing import Optional, Union


def get_chat_model(
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    api_key: Optional[str] = None
) -> Union["MockChatModel", "RealChatModel"]:
    api_key = api_key or os.getenv("OPENAI_API_KEY", "")
    
    if not api_key:
        return MockChatModel(
            model_name=model_name or os.getenv("LLM_MODEL", "gpt-4"),
            temperature=temperature,
        )
    
    return RealChatModel(
        model_name=model_name or os.getenv("OPENAI_MODEL_NAME", "gpt-4"),
        temperature=temperature,
        api_key=api_key,
        base_url=os.getenv("OPENAI_API_BASE") or None,
    )


class MockChatModel:
    def __init__(self, model_name: str, temperature: float):
        self.model_name = model_name
        self.temperature = temperature

    def invoke(self, messages: list[dict]) -> str:
        return f"Mock response for: {messages[-1].get('content', '')}"

    def with_structured_output(self, schema: type):
        return MockStructuredOutput(schema)


class RealChatModel:
    def __init__(self, model_name: str, temperature: float, api_key: str, base_url: Optional[str] = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name
        self.temperature = temperature

    def invoke(self, messages: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
        )
        return response.choices[0].message.content

    def with_structured_output(self, schema: type):
        raise NotImplementedError("RealChatModel with_structured_output not implemented")


class MockStructuredOutput:
    def __init__(self, schema: type):
        self.schema = schema

    def invoke(self, messages: list[dict]) -> dict:
        return {
            "intent": "faq",
            "confidence": 0.85,
        }
