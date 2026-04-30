import time
import httpx
from dataclasses import dataclass

@dataclass
class LLMResult:
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float

async def call_llm(prompt: str, max_tokens: int = 512) -> LLMResult:
    start = time.time()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "tinyllama",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

    data = response.json()
    latency = (time.time() - start) * 1000

    return LLMResult(
        text=data["response"],
        model="tinyllama",
        prompt_tokens=0,
        completion_tokens=0,
        latency_ms=latency
    )
