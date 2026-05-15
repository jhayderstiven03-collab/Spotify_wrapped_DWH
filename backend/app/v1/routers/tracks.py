"""
filename: tracks.py
author: CAMILO TORRES
date: 2026-05-14
version: 1.0
description: Router for top tracks endpoint. Returns data from dwh.dim_tracks.
"""

from fastapi import APIRouter, Depends
from backend.app.core.security import get_current_user
from backend.app.v1.services.tracks_service import get_top_tracks
from backend.app.v1.schemas.tracks import TrackResponse

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.get("/top", response_model=list[TrackResponse])
def top_tracks(spotify_id: str = Depends(get_current_user)):
    """
    Returns top tracks from the DWH.

    Args:
        spotify_id (str): Extracted from the JWT by get_current_user.

    Returns:
        list[TrackResponse]: List of top tracks.
    """
    return get_top_tracks()