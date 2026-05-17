"""
filename: test_tracks.py
author: CAMILO TORRES
date: 2026-05-15
version: 1.0
description: Unit tests for the tracks router.
"""

from unittest.mock import patch
from datetime import datetime


MOCK_TRACKS = [
    {
        "track_id": 1,
        "spotify_id": "track_abc123",
        "name": "Tití Me Preguntó",
        "artist_id": 1,
        "album_name": "Un Verano Sin Ti",
        "duration_ms": 198013,
        "popularity": 95,
        "explicit": True,
        "loaded_at": datetime(2026, 5, 15, 10, 0, 0),
        "play_count": 10,
    }
]


def test_get_top_tracks_returns_200(client, auth_headers):
    """GET /v1/tracks/top should return 200 with valid token."""
    with patch("backend.app.v1.routers.tracks.get_top_tracks", return_value=MOCK_TRACKS):
        response = client.get("/v1/tracks/top", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Tití Me Preguntó"


def test_get_top_tracks_without_token_returns_401(client):
    """GET /v1/tracks/top without token should return 401."""
    response = client.get("/v1/tracks/top")
    assert response.status_code == 401


def test_get_top_tracks_with_invalid_token_returns_401(client):
    """GET /v1/tracks/top with invalid token should return 401."""
    response = client.get(
        "/v1/tracks/top",
        headers={"Authorization": "Bearer token_invalido"}
    )
    assert response.status_code == 401


def test_get_top_tracks_returns_list(client, auth_headers):
    """GET /v1/tracks/top should return a list."""
    with patch("backend.app.v1.routers.tracks.get_top_tracks", return_value=MOCK_TRACKS):
        response = client.get("/v1/tracks/top", headers=auth_headers)
    assert isinstance(response.json(), list)