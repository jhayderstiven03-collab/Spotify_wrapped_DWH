"""
filename: tracks_service.py
author: CAMILO TORRES
date: 2026-05-14
version: 1.0
description: Service for fetching top tracks data from dwh.dim_tracks.
"""

from backend.app.core.database import get_connection


def get_top_tracks() -> list[dict]:
    """
    Fetches all tracks from dwh.dim_tracks ordered by popularity.

    Returns:
        list[dict]: List of track records.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM dwh.dim_tracks ORDER BY popularity DESC LIMIT 50"
            )
            return cur.fetchall()
    finally:
        conn.close()