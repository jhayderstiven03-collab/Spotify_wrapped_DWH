"""
filename: artists.py
author: CAMILO TORRES
date: 2026-05-14
version: 1.0
description: Pydantic schemas for top artists endpoint.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ArtistBase(BaseModel):
    spotify_id: str
    name: str
    popularity: int | None
    followers_count: int | None
    genres: list[str] | None


class ArtistRequest(ArtistBase):
    pass


class ArtistResponse(ArtistBase):
    artist_id: int
    loaded_at: datetime

    model_config = ConfigDict(from_attributes=True)