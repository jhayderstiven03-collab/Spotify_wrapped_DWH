"""
filename: profile.py
author: CAMILO TORRES
date: 2026-05-14
version: 1.0
description: Router for user profile endpoint. Returns profile data from dwh.dim_users.
"""

from fastapi import APIRouter, Depends, HTTPException
from backend.app.core.security import get_current_user
from backend.app.v1.services.profile_service import get_user_profile
from backend.app.v1.schemas.profile import ProfileResponse

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=ProfileResponse)
def get_profile(spotify_id: str = Depends(get_current_user)):
    """
    Returns the authenticated user's profile from the DWH.

    Args:
        spotify_id (str): Extracted from the JWT by get_current_user.

    Returns:
        ProfileResponse: User profile data.
    """
    profile = get_user_profile(spotify_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Run ETL first.")
    return profile