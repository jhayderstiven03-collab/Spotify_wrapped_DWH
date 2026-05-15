"""
filename: history.py
author: CAMILO TORRES
date: 2026-05-14
version: 1.0
description: Router for recently played history endpoint.
"""

from fastapi import APIRouter, Depends
from backend.app.core.security import get_current_user
from backend.app.v1.services.history_service import get_recently_played
from backend.app.v1.schemas.history import HistoryResponse

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/recently-played", response_model=list[HistoryResponse])
def recently_played(spotify_id: str = Depends(get_current_user)):
    """
    Returns the authenticated user's listening history from the DWH.

    Args:
        spotify_id (str): Extracted from the JWT by get_current_user.

    Returns:
        list[HistoryResponse]: List of recently played tracks.
    """
    return get_recently_played(spotify_id)