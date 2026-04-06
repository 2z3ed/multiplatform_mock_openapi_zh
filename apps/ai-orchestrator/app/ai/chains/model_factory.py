"""Model factory for AI layer."""

import os
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)


def get_chat_model(
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    api_key: Optional[str] = None
) -> Union["MockChatModel", "RealChatModel"]:
    api_key = api_key or os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_API_BASE") or None
    model = model_name or os.getenv("OPENAI_MODEL_NAME") or os.getenv("LLM_MODEL", "gpt-4")
    
    logger.info(f"Model factory - API Key set: {bool(api_key)}, Base URL: {base_url}, Model: {model}")
    
    if not api_key:
        logger.warning("No OPENAI_API_KEY found, using MockChatModel")
        return MockChatModel(
            model_name=model,
            temperature=temperature,
        )
    
    logger.info(f"Using RealChatModel with model: {model}")
    return RealChatModel(
        model_name=model,
        temperature=temperature,
        api_key=api_key,
        base_url=base_url,
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
    LLM_TIMEOUT = 10.0

    def __init__(self, model_name: str, temperature: float, api_key: str, base_url: Optional[str] = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=base_url, max_retries=0, timeout=10.0)
        self.model_name = model_name
        self.temperature = temperature
        logger.info(f"RealChatModel initialized - model: {model_name}, timeout: {self.LLM_TIMEOUT}s")

    def invoke(self, messages: list[dict]) -> str:
        import signal

        class TimeoutError(Exception):
            pass

        def _handler(signum, frame):
            raise TimeoutError(f"LLM call timed out after {self.LLM_TIMEOUT}s")

        old_handler = signal.signal(signal.SIGALRM, _handler)
        signal.alarm(int(self.LLM_TIMEOUT))

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
            )
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
            return response.choices[0].message.content
        except TimeoutError as e:
            logger.warning(f"LLM call timed out - model: {self.model_name}, timeout: {self.LLM_TIMEOUT}s")
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
            raise
        except Exception as e:
            logger.warning(f"LLM call failed - model: {self.model_name}, error: {type(e).__name__}: {e}")
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
            raise

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
