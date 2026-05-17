"""
filename: test_auth.py
author: CAMILO TORRES
date: 2026-05-15
version: 1.0
description: Unit tests for the auth router.
"""

from unittest.mock import patch


def test_login_redirects_to_spotify(client):
    """GET /v1/auth/login should redirect to Spotify authorization URL."""
    response = client.get("/v1/auth/login", follow_redirects=False)
    assert response.status_code in [302, 307]
    assert "accounts.spotify.com" in response.headers["location"]


def test_callback_with_invalid_state_returns_400(client):
    """GET /v1/auth/callback with unknown state should return 400."""
    response = client.get(
        "/v1/auth/callback",
        params={"code": "fake_code", "state": "invalid_state_that_doesnt_exist"}
    )
    assert response.status_code == 400