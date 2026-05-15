"""
filename: etl.py
author: Jhayder Florez
date: 2026-05-15
version: 1.0
description: Router for ETL endpoints. Triggers the pipeline and returns execution status.
"""

from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
import requests

from backend.app.core.config import settings
from backend.app.core.database import get_connection
from backend.app.core.security import get_current_user
from backend.app.v1.services.etl_service import run_etl

router = APIRouter(prefix="/etl", tags=["etl"])

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"


def _get_valid_spotify_token(spotify_id: str, conn) -> str:
    """
    Returns a valid Spotify access token, refreshing it if needed.

    Args:
        spotify_id (str): Spotify user ID.
        conn: Active psycopg2 connection.

    Returns:
        str: Valid Spotify access token.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT spotify_access_token, spotify_refresh_token, token_expires_at
            FROM dwh.dim_users
            WHERE spotify_id = %s
        """, (spotify_id,))
        row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="User not found. Login first.")

    expires_at = row["token_expires_at"]
    now = datetime.now(timezone.utc)

    # Renovar si expira en menos de 5 minutos
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now + timedelta(minutes=5):
        response = requests.post(
            SPOTIFY_TOKEN_URL,
            data={
                "grant_type":    "refresh_token",
                "refresh_token": row["spotify_refresh_token"],
                "client_id":     settings.SPOTIFY_CLIENT_ID,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Could not refresh Spotify token")

        new_data = response.json()
        new_token      = new_data["access_token"]
        new_expires_at = now + timedelta(seconds=new_data["expires_in"])

        with conn.cursor() as cur:
            cur.execute("""
                UPDATE dwh.dim_users
                SET spotify_access_token = %s, token_expires_at = %s
                WHERE spotify_id = %s
            """, (new_token, new_expires_at, spotify_id))
        conn.commit()

        return new_token

    return row["spotify_access_token"]


@router.post("/run")
def run_etl_endpoint(spotify_id: str = Depends(get_current_user)):
    """
    Triggers the full ETL pipeline for the authenticated user.

    Args:
        spotify_id (str): Extracted from the JWT by get_current_user.

    Returns:
        dict: ETL execution summary with steps and metrics.
    """
    conn = get_connection()
    try:
        spotify_token = _get_valid_spotify_token(spotify_id, conn)
    finally:
        conn.close()

    return run_etl(spotify_token, spotify_id)


@router.get("/status")
def etl_status(spotify_id: str = Depends(get_current_user)):
    """
    Returns the current DWH table counts and last 10 ETL runs.

    Args:
        spotify_id (str): Extracted from the JWT by get_current_user.

    Returns:
        dict: Table record counts and recent ETL audit history.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Conteo de cada tabla
            cur.execute("SELECT COUNT(*) as count FROM dwh.dim_users")
            users_count = cur.fetchone()["count"]

            cur.execute("SELECT COUNT(*) as count FROM dwh.dim_artists")
            artists_count = cur.fetchone()["count"]

            cur.execute("SELECT COUNT(*) as count FROM dwh.dim_tracks")
            tracks_count = cur.fetchone()["count"]

            cur.execute("SELECT COUNT(*) as count FROM dwh.fact_listening_history")
            history_count = cur.fetchone()["count"]

            # Últimas 10 ejecuciones del ETL
            cur.execute("""
                SELECT audit_id, started_at, finished_at, duration_ms,
                       status, history_new, artists_new, tracks_new, error_message
                FROM dwh.etl_audit
                WHERE spotify_user_id = %s
                ORDER BY started_at DESC
                LIMIT 10
            """, (spotify_id,))
            last_runs = cur.fetchall()

        return {
            "tables": [
                {"name": "dim_users",             "record_count": users_count},
                {"name": "dim_artists",           "record_count": artists_count},
                {"name": "dim_tracks",            "record_count": tracks_count},
                {"name": "fact_listening_history","record_count": history_count},
            ],
            "last_runs": [dict(r) for r in last_runs]
        }
    finally:
        conn.close()