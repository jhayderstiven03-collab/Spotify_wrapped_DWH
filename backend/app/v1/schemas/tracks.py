"""
filename: tracks.py
author: CAMILO TORRES
date: 2026-05-14
version: 1.0
description: Pydantic schemas for top tracks endpoint.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TrackBase(BaseModel):
    spotify_id: str
    name: str
    artist_id: int | None
    album_name: str | None
    duration_ms: int | None
    popularity: int | None
    explicit: bool | None


class TrackRequest(TrackBase):
    pass


class TrackResponse(TrackBase):
    track_id: int
    loaded_at: datetime

    model_config = ConfigDict(from_attributes=True)