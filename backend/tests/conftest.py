"""
filename: conftest.py
author: CAMILO TORRES
date: 2026-05-15
version: 1.0
description: Shared fixtures for all tests. Provides a TestClient and a valid mock JWT.
"""

import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from jose import jwt

from backend.app.main import app
from backend.app.core.config import settings


@pytest.fixture
def client():
    """
    Returns a FastAPI TestClient for the app.

    Returns:
        TestClient: Test client instance.
    """
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def valid_token():
    """
    Generates a valid mock JWT for testing protected endpoints.

    Returns:
        str: Encoded JWT with spotify_id = 'test_user_123'.
    """
    payload = {
        "sub": "test_user_123",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


@pytest.fixture
def auth_headers(valid_token):
    """
    Returns Authorization headers with the mock JWT.

    Returns:
        dict: Headers dictionary with Bearer token.
    """
    return {"Authorization": f"Bearer {valid_token}"}