"""
filename: spotify_client.py
author: Jhayder FLorez
date: 2025-05-15
version: 1.0
description: Cliente HTTP reutilizable para consumir la Spotify Web API con autenticación Bearer.
"""

import requests

BASE_URL = "https://api.spotify.com/v1"


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def get_user_profile(token: str) -> dict:
    """
    Obtiene el perfil del usuario autenticado desde la Spotify API.

    Args:
        token (str): Access token de Spotify (Bearer).

    Returns:
        dict: Objeto de perfil del usuario en formato JSON crudo de Spotify.
    """
    r = requests.get(f"{BASE_URL}/me", headers=_headers(token))
    r.raise_for_status()
    return r.json()


def get_top_artists(token: str) -> list[dict]:
    """
    Obtiene los top artistas del usuario desde la Spotify API.

    Args:
        token (str): Access token de Spotify (Bearer).

    Returns:
        list[dict]: Lista de objetos artista en formato JSON crudo de Spotify.
    """
    r = requests.get(
        f"{BASE_URL}/me/top/artists",
        headers=_headers(token),
        params={"limit": 50, "time_range": "medium_term"},
    )
    r.raise_for_status()
    return r.json()["items"]


def get_top_tracks(token: str) -> list[dict]:
    """
    Obtiene los top tracks del usuario desde la Spotify API.

    Args:
        token (str): Access token de Spotify (Bearer).

    Returns:
        list[dict]: Lista de objetos track en formato JSON crudo de Spotify.
    """
    r = requests.get(
        f"{BASE_URL}/me/top/tracks",
        headers=_headers(token),
        params={"limit": 50, "time_range": "medium_term"},
    )
    r.raise_for_status()
    return r.json()["items"]


def get_recently_played(token: str, after_ms: int | None = None) -> list[dict]:
    """
    Obtiene el historial de reproducciones recientes del usuario.

    Args:
        token (str): Access token de Spotify (Bearer).
        after_ms (int | None): Cursor Unix ms. Si se provee, retorna solo
                               reproducciones después de ese momento. None = primera carga.

    Returns:
        list[dict]: Lista de PlayHistoryObjects en formato JSON crudo de Spotify.
    """
    params: dict = {"limit": 50}
    if after_ms is not None:
        params["after"] = after_ms

    r = requests.get(
        f"{BASE_URL}/me/player/recently-played",
        headers=_headers(token),
        params=params,
    )
    r.raise_for_status()
    return r.json()["items"]