"""
filename: artists_service.py
author: CAMILO TORRES
date: 2026-05-14
version: 1.0
description: Service for fetching top artists data from dwh.dim_artists.
"""

from backend.app.core.database import get_connection


def get_top_artists() -> list[dict]:
    """
    Fetches all artists from dwh.dim_artists ordered by popularity.

    Returns:
        list[dict]: List of artist records.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM dwh.dim_artists ORDER BY popularity DESC LIMIT 50"
            )
            return cur.fetchall()
    finally:
        conn.close()