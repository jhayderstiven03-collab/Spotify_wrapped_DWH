"""
filename: history.py
author: CAMILO TORRRES
date: 2026-05-14
version: 1.0
description: Pydantic schemas for recently played history endpoint.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class HistoryBase(BaseModel):
    user_id: int
    track_id: int
    artist_id: int
    played_at: datetime
    hour_of_day: int | None
    day_of_week: str | None
    context_type: str | None


class HistoryRequest(HistoryBase):
    pass


class HistoryResponse(HistoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)