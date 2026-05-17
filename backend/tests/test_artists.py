"""
filename: test_artists.py
author: CAMILO TORRES
date: 2026-05-15
version: 1.0
description: Unit tests for the artists router.
"""

from unittest.mock import patch
from datetime import datetime


MOCK_ARTISTS = [
    {
        "artist_id": 1,
        "spotify_id": "artist_abc123",
        "name": "Bad Bunny",
        "popularity": 98,
        "followers_count": 50000000,
        "genres": ["reggaeton", "latin trap"],
        "loaded_at": datetime(2026, 5, 15, 10, 0, 0),
        "play_count": 25,
    }
]


def test_get_top_artists_returns_200(client, auth_headers):
    """GET /v1/artists/top should return 200 with valid token."""
    with patch("backend.app.v1.routers.artists.get_top_artists", return_value=MOCK_ARTISTS):
        response = client.get("/v1/artists/top", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Bad Bunny"


def test_get_top_artists_without_token_returns_401(client):
    """GET /v1/artists/top without token should return 401."""
    response = client.get("/v1/artists/top")
    assert response.status_code == 401


def test_get_top_artists_with_invalid_token_returns_401(client):
    """GET /v1/artists/top with invalid token should return 401."""
    response = client.get(
        "/v1/artists/top",
        headers={"Authorization": "Bearer token_invalido"}
    )
    assert response.status_code == 401


def test_get_top_artists_returns_list(client, auth_headers):
    """GET /v1/artists/top should return a list."""
    with patch("backend.app.v1.routers.artists.get_top_artists", return_value=MOCK_ARTISTS):
        response = client.get("/v1/artists/top", headers=auth_headers)
    assert isinstance(response.json(), list)