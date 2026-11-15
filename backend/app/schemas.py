from __future__ import annotations
from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Status(str, Enum):
    VERIFIED_CURRENT = "VERIFIED_CURRENT"
    POTENTIALLY_OUTDATED = "POTENTIALLY_OUTDATED"
    CONTRADICTED = "CONTRADICTED"
    UNVERIFIABLE = "UNVERIFIABLE"
    STALE = "STALE"
    NOT_TIME_SENSITIVE = "NOT_TIME_SENSITIVE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class Volatility(str, Enum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    STABLE = "stable"


class Stance(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    NEUTRAL = "neutral"


class Claim(BaseModel):
    id: str
    original_text: str
    normalized: str
    category: str = "Other"
    entities: list[str] = []
    dates: list[str] = []
    numbers: list[str] = []
    volatility: Volatility = Volatility.MEDIUM
    time_sensitive: bool = True
    depends_on: list[str] = []


class Source(BaseModel):
    title: str
    url: str
    domain: str
    published_date: Optional[date] = None
    published_date_inferred: bool = False
    retrieved_at: datetime
    excerpt: str
    source_type: str = "other"
    authority: float = Field(ge=0, le=1, default=0.4)
    relevance: float = Field(ge=0, le=1, default=0.5)
    stance: Stance = Stance.NEUTRAL
    from_cache: bool = False
    simulated: bool = False


class ClaimResult(BaseModel):
    claim: Claim
    status: Status
    freshness_score: Optional[int] = None  # None when no reliable dates
    evidence_confidence: float = 0.0
    source_reliability: float = 0.0
    explanation: str
    sources: list[Source] = []
    conflict: bool = False
    suggested_correction: Optional[str] = None
    alerts: list[str] = []
    queries: list[str] = []


class VerifyRequest(BaseModel):
    answer: str = Field(min_length=10, max_length=8000)
    as_of: Optional[date] = None
    max_results: int = Field(default=5, ge=1, le=10)
    max_claims: int = Field(default=12, ge=1, le=25)


class VerificationResult(BaseModel):
    id: str
    created_at: datetime
    mode: str  # "live" or "demo"
    notice: str
    answer: str
    as_of: date
    claims: list[ClaimResult]
    summary: dict
    verified_answer: Optional[str] = None
    changes: list[dict] = []
    warnings: list[str] = []
