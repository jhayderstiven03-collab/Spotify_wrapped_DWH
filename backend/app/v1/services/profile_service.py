"""
filename: profile_service.py
author: CAMILO TORRES
date: 2026-05-14
version: 1.0
description: Service for fetching user profile data from dwh.dim_users.
"""

from backend.app.core.database import get_connection


def get_user_profile(spotify_id: str) -> dict | None:
    """
    Fetches the user profile from dwh.dim_users by spotify_id.

    Args:
        spotify_id (str): The Spotify user ID from the JWT.

    Returns:
        dict | None: User profile data or None if not found.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM dwh.dim_users WHERE spotify_id = %s",
                (spotify_id,)
            )
            return cur.fetchone()
    finally:
        conn.close()