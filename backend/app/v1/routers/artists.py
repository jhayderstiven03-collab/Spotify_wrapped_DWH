"""
filename: artists.py
author: CAMILO TORRES
date: 2026-05-14
version: 1.0
description: Router for top artists endpoint. Returns data from dwh.dim_artists.
"""

from fastapi import APIRouter, Depends
from backend.app.core.security import get_current_user
from backend.app.v1.services.artists_service import get_top_artists
from backend.app.v1.schemas.artists import ArtistResponse

router = APIRouter(prefix="/artists", tags=["artists"])


@router.get("/top", response_model=list[ArtistResponse])
def top_artists(spotify_id: str = Depends(get_current_user)):
    """
    Returns top artists from the DWH.

    Args:
        spotify_id (str): Extracted from the JWT by get_current_user.

    Returns:
        list[ArtistResponse]: List of top artists.
    """
    return get_top_artists()