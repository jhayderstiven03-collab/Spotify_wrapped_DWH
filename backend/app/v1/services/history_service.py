"""
filename: history_service.py
author: CAMILO TORRES
date: 2026-05-14
version: 1.0
description: Service for fetching listening history from dwh.fact_listening_history.
"""

from backend.app.core.database import get_connection


def get_recently_played(spotify_id: str) -> list[dict]:
    """
    Fetches the listening history for the authenticated user.

    Args:
        spotify_id (str): The Spotify user ID from the JWT.

    Returns:
        list[dict]: List of listening history records ordered by played_at desc.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT f.*
                FROM dwh.fact_listening_history f
                JOIN dwh.dim_users u ON u.user_id = f.user_id
                WHERE u.spotify_id = %s
                ORDER BY f.played_at DESC
                LIMIT 50
            """, (spotify_id,))
            return cur.fetchall()
    finally:
        conn.close()

def get_peak_hour(spotify_id: str) -> dict:
    """
    Returns the hour of day with most reproductions for the user.

    Args:
        spotify_id (str): The Spotify user ID from the JWT.

    Returns:
        dict: {"hour": int, "count": int} or None if no data.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT f.hour_of_day, COUNT(*) as count
                FROM dwh.fact_listening_history f
                JOIN dwh.dim_users u ON u.user_id = f.user_id
                WHERE u.spotify_id = %s
                GROUP BY f.hour_of_day
                ORDER BY count DESC
                LIMIT 1
            """, (spotify_id,))
            row = cur.fetchone()
            if not row:
                return None
            return {"hour": row["hour_of_day"], "count": row["count"]}
    finally:
        conn.close()