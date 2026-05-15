"""
filename: etl_service.py
author: Jhayder Florez
date: 2026-05-15
version: 1.0
description: ETL pipeline service. Orchestrates the three phases (Extract, Transform, Load)
             for all four Spotify endpoints into the DWH.
"""

import time
from datetime import datetime, timezone

from backend.app.core.database import get_connection
from backend.app.core.spotify_client import (
    get_user_profile,
    get_top_artists,
    get_top_tracks,
    get_recently_played,
)


# ─────────────────────────────────────────────
# EXTRACT
# ─────────────────────────────────────────────

def extract_user(token: str) -> dict:
    """
    Extracts raw user profile data from Spotify.

    Args:
        token (str): Spotify access token.

    Returns:
        dict: Raw user profile JSON from Spotify.
    """
    return get_user_profile(token)


def extract_top_artists(token: str) -> list[dict]:
    """
    Extracts raw top artists data from Spotify.

    Args:
        token (str): Spotify access token.

    Returns:
        list[dict]: Raw list of top artist objects from Spotify.
    """
    return get_top_artists(token)


def extract_top_tracks(token: str) -> list[dict]:
    """
    Extracts raw top tracks data from Spotify.

    Args:
        token (str): Spotify access token.

    Returns:
        list[dict]: Raw list of top track objects from Spotify.
    """
    return get_top_tracks(token)


def extract_recently_played(token: str, after_ms: int | None = None) -> list[dict]:
    """
    Extracts raw recently played history from Spotify.

    Args:
        token (str): Spotify access token.
        after_ms (int | None): Cursor in Unix ms. Only returns tracks after this moment.

    Returns:
        list[dict]: Raw list of PlayHistoryObject from Spotify.
    """
    return get_recently_played(token, after_ms)


# ─────────────────────────────────────────────
# TRANSFORM
# ─────────────────────────────────────────────

def transform_user(raw: dict) -> dict:
    """
    Normalizes raw Spotify user profile into a dwh.dim_users-ready dict.

    Args:
        raw (dict): Raw user profile JSON from Spotify.

    Returns:
        dict: Normalized user data matching dwh.dim_users columns.
    """
    return {
        "spotify_id":   raw["id"],
        "display_name": raw.get("display_name"),
        "email":        raw.get("email"),
        "country":      raw.get("country"),
        "followers":    raw.get("followers", {}).get("total", 0),
        "product":      raw.get("product"),
    }


def transform_artists(raw_list: list[dict]) -> list[dict]:
    """
    Normalizes a list of raw Spotify artist objects into dwh.dim_artists-ready dicts.

    Args:
        raw_list (list[dict]): Raw list of artist objects from Spotify.

    Returns:
        list[dict]: Normalized artist data matching dwh.dim_artists columns.
    """
    result = []
    for item in raw_list:
        result.append({
            "spotify_id":      item["id"],
            "name":            item["name"],
            "popularity":      item.get("popularity"),
            "followers_count": item.get("followers", {}).get("total", 0),
            "genres":          item.get("genres", []),
        })
    return result


def transform_tracks(raw_list: list[dict]) -> list[dict]:
    """
    Normalizes a list of raw Spotify track objects into dwh.dim_tracks-ready dicts.

    Args:
        raw_list (list[dict]): Raw list of track objects from Spotify.

    Returns:
        list[dict]: Normalized track data matching dwh.dim_tracks columns.
    """
    result = []
    for item in raw_list:
        result.append({
            "spotify_id":       item["id"],
            "name":             item["name"],
            "artist_spotify_id": item["artists"][0]["id"] if item.get("artists") else None,
            "album_name":       item.get("album", {}).get("name"),
            "duration_ms":      item.get("duration_ms"),
            "popularity":       item.get("popularity"),
            "explicit":         item.get("explicit", False),
        })
    return result


def transform_history(raw_list: list[dict]) -> list[dict]:
    """
    Normalizes a list of raw Spotify PlayHistoryObjects into
    dwh.fact_listening_history-ready dicts.

    Args:
        raw_list (list[dict]): Raw list of PlayHistoryObject from Spotify.

    Returns:
        list[dict]: Normalized history data matching dwh.fact_listening_history columns.
    """
    result = []
    for item in raw_list:
        played_at_str = item["played_at"]
        played_at = datetime.fromisoformat(played_at_str.replace("Z", "+00:00"))

        result.append({
            "track_spotify_id":  item["track"]["id"],
            "artist_spotify_id": item["track"]["artists"][0]["id"] if item["track"].get("artists") else None,
            "played_at":         played_at,
            "hour_of_day":       played_at.hour,
            "day_of_week":       played_at.strftime("%A"),
            "context_type":      (item.get("context") or {}).get("type") or "unknown",
        })
    return result