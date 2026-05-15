"""
filename: spotify_client.py
author: Jhayder Florez
date: 2026-05-15
version: 1.0
description: Reusable HTTP client for Spotify Web API. Handles all requests
             to Spotify endpoints used by the ETL pipeline.
"""

import requests
from fastapi import HTTPException

SPOTIFY_BASE_URL = "https://api.spotify.com/v1"


def _get_headers(token: str) -> dict:
    """
    Builds the Authorization header for Spotify API requests.

    Args:
        token (str): Spotify access token.

    Returns:
        dict: Header dictionary with Bearer token.
    """
    return {"Authorization": f"Bearer {token}"}


def get_user_profile(token: str) -> dict:
    """
    Calls GET /v1/me and returns the raw user profile from Spotify.

    Args:
        token (str): Spotify access token.

    Returns:
        dict: Raw user profile JSON from Spotify.
    """
    response = requests.get(
        f"{SPOTIFY_BASE_URL}/me",
        headers=_get_headers(token)
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Spotify /me error: {response.text}"
        )
    return response.json()


def get_top_artists(token: str) -> list[dict]:
    """
    Calls GET /v1/me/top/artists and returns the raw artist list from Spotify.

    Args:
        token (str): Spotify access token.

    Returns:
        list[dict]: Raw list of top artist objects from Spotify.
    """
    response = requests.get(
        f"{SPOTIFY_BASE_URL}/me/top/artists",
        headers=_get_headers(token),
        params={"limit": 50, "time_range": "medium_term"}
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Spotify /me/top/artists error: {response.text}"
        )
    return response.json().get("items", [])


def get_top_tracks(token: str) -> list[dict]:
    """
    Calls GET /v1/me/top/tracks and returns the raw track list from Spotify.

    Args:
        token (str): Spotify access token.

    Returns:
        list[dict]: Raw list of top track objects from Spotify.
    """
    response = requests.get(
        f"{SPOTIFY_BASE_URL}/me/top/tracks",
        headers=_get_headers(token),
        params={"limit": 50, "time_range": "medium_term"}
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Spotify /me/top/tracks error: {response.text}"
        )
    return response.json().get("items", [])


def get_recently_played(token: str, after_ms: int | None = None) -> list[dict]:
    """
    Calls GET /v1/me/player/recently-played and returns the raw play history.

    Args:
        token (str): Spotify access token.
        after_ms (int | None): Unix timestamp in milliseconds. If provided,
                               only returns tracks played after this moment.

    Returns:
        list[dict]: Raw list of PlayHistoryObject from Spotify.
    """
    params = {"limit": 50}
    if after_ms is not None:
        params["after"] = after_ms

    response = requests.get(
        f"{SPOTIFY_BASE_URL}/me/player/recently-played",
        headers=_get_headers(token),
        params=params
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Spotify /recently-played error: {response.text}"
        )
    return response.json().get("items", [])