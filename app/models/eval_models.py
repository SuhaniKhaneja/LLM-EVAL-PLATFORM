import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

def utcnow():
    return datetime.now(timezone.utc)

class Prompt(Base):
    __tablename__ = "prompts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                     default=lambda: str(uuid.uuid4()))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    response: Mapped["Response"] = relationship("Response", back_populates="prompt",
                                                 uselist=False, cascade="all, delete-orphan")

class Response(Base):
    __tablename__ = "responses"
    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                     default=lambda: str(uuid.uuid4()))
    prompt_id: Mapped[str] = mapped_column(String(36), ForeignKey("prompts.id"), index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(64))
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    prompt: Mapped["Prompt"] = relationship("Prompt", back_populates="response")
    evaluation: Mapped["EvalResult"] = relationship("EvalResult", back_populates="response",
                                                      uselist=False, cascade="all, delete-orphan")

class EvalResult(Base):
    __tablename__ = "eval_results"
    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                     default=lambda: str(uuid.uuid4()))
    response_id: Mapped[str] = mapped_column(String(36), ForeignKey("responses.id"), index=True)
    length_score: Mapped[float] = mapped_column(Float, default=0.0)
    rouge1_score: Mapped[float] = mapped_column(Float, default=0.0)
    toxicity_score: Mapped[float] = mapped_column(Float, default=1.0)
    is_toxic: Mapped[bool] = mapped_column(default=False)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    response: Mapped["Response"] = relationship("Response", back_populates="evaluation")