"""
filename: test_profile.py
author: CAMILO TORRES
date: 2026-05-15
version: 1.0
description: Unit tests for the profile router.
"""

from unittest.mock import patch
from datetime import datetime


MOCK_PROFILE = {
    "user_id": 1,
    "spotify_id": "test_user_123",
    "display_name": "Test User",
    "email": "test@example.com",
    "country": "CO",
    "followers": 100,
    "product": "premium",
    "loaded_at": datetime(2026, 5, 15, 10, 0, 0),
}


def test_get_profile_returns_200(client, auth_headers):
    """GET /v1/profile/me should return 200 with valid token."""
    with patch("backend.app.v1.routers.profile.get_user_profile", return_value=MOCK_PROFILE):
        response = client.get("/v1/profile/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["spotify_id"] == "test_user_123"


def test_get_profile_without_token_returns_401(client):
    """GET /v1/profile/me without token should return 401."""
    response = client.get("/v1/profile/me")
    assert response.status_code == 401


def test_get_profile_with_invalid_token_returns_401(client):
    """GET /v1/profile/me with invalid token should return 401."""
    response = client.get(
        "/v1/profile/me",
        headers={"Authorization": "Bearer token_invalido"}
    )
    assert response.status_code == 401


def test_get_profile_not_found_returns_404(client, auth_headers):
    """GET /v1/profile/me should return 404 if user not in DWH."""
    with patch("backend.app.v1.routers.profile.get_user_profile", return_value=None):
        response = client.get("/v1/profile/me", headers=auth_headers)
    assert response.status_code == 404