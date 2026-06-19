import time
import os
from openai import AsyncOpenAI
from dataclasses import dataclass

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@dataclass
class LLMResult:
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float


async def call_llm(prompt: str, max_tokens: int = 512) -> LLMResult:
    start = time.time()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    latency = (time.time() - start) * 1000
    return LLMResult(
        text=response.choices[0].message.content,
        model="gpt-4o-mini",
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
        latency_ms=latency,
    )
