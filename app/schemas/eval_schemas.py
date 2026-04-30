from datetime import datetime
from pydantic import BaseModel, Field

class EvaluateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)
    reference: str = Field(default="", description="Optional reference text for ROUGE scoring")
    max_tokens: int = Field(default=512, ge=1, le=4096)

class ScoresOut(BaseModel):
    length_score: float
    rouge1_score: float
    toxicity_score: float
    is_toxic: bool
    overall_score: float

class EvaluateResponse(BaseModel):
    prompt_id: str
    response_id: str
    evaluation_id: str
    prompt: str
    response: str
    model: str
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    scores: ScoresOut
    created_at: datetime

class LogEntry(BaseModel):
    prompt_id: str
    response_id: str
    evaluation_id: str
    prompt: str
    response: str
    model: str
    latency_ms: float
    overall_score: float
    is_toxic: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class PaginatedLogs(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[LogEntry]

class MetricsOut(BaseModel):
    total_evaluations: int
    avg_overall_score: float
    avg_latency_ms: float
    toxic_count: int
    toxic_rate: float
    avg_rouge1: float
    score_distribution: dict[str, int]