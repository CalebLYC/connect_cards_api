from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from uuid import UUID


class DailyScanSchema(BaseModel):
    day: date
    count: int


class TopCardSchema(BaseModel):
    card_id: UUID
    count: int
    card_name: Optional[str] = None


class DenialRateSchema(BaseModel):
    total_scans: int
    denied_scans: int
    denial_rate: float  # (denied_scans / total_scans) * 100


class AnalyticsSummarySchema(BaseModel):
    organization_id: UUID
    start_date: date
    end_date: date
    daily_scans: List[DailyScanSchema]
    top_cards: List[TopCardSchema]
    denial_metrics: DenialRateSchema
