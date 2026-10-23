
import time
from dataclasses import dataclass

from openai import AsyncOpenAI

from app.core.config import get_settings


settings = get_settings()

client = AsyncOpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1",
    timeout=60.0,
    max_retries=2,
)


@dataclass
class LLMResult:
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float


async def call_llm(
    prompt: str,
    max_tokens: int = 512,
) -> LLMResult:
    """Call the configured Groq model and return its response and usage data."""

    start = time.perf_counter()

    response = await client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )

    latency_ms = (time.perf_counter() - start) * 1000

    if not response.choices:
        raise RuntimeError("The LLM provider returned no response choices.")

    message = response.choices[0].message
    usage = response.usage

    return LLMResult(
        text=message.content or "",
        model=response.model or settings.groq_model,
        prompt_tokens=usage.prompt_tokens if usage else 0,
        completion_tokens=usage.completion_tokens if usage else 0,
        latency_ms=round(latency_ms, 2),
    )
