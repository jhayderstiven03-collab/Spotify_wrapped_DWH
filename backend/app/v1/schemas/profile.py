"""
filename: profile.py
author: CAMILO TORRES
date: 2026-05-14
version: 1.0
description: Pydantic schemas for user profile endpoint.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProfileBase(BaseModel):
    spotify_id: str
    display_name: str | None
    email: str | None
    country: str | None
    followers: int | None
    product: str | None


class ProfileRequest(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    user_id: int
    loaded_at: datetime

    model_config = ConfigDict(from_attributes=True)