"""
filename: auth.py
author: CAMILO TOORES
date: 2026-05-13
version: 1.0
description: Router de autenticación. Maneja el flujo OAuth PKCE con Spotify
             y la emisión del JWT de la app.
"""

import os
import hashlib
import base64
import uuid
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode

import requests
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from jose import jwt

from backend.app.core.config import settings
from backend.app.core.database import get_connection

router = APIRouter(prefix="/auth", tags=["auth"])

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_ME_URL = "https://api.spotify.com/v1/me"
SCOPES = "user-read-private user-read-email user-top-read user-read-recently-played"


def _generate_pkce() -> tuple[str, str]:
    """
    Genera el par code_verifier y code_challenge para el flujo PKCE.

    Returns:
        tuple[str, str]: (code_verifier, code_challenge)
    """
    code_verifier = base64.urlsafe_b64encode(os.urandom(64)).rstrip(b"=").decode("utf-8")
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("utf-8")
    return code_verifier, code_challenge


@router.get("/login")
def spotify_login():
    """
    Inicia el flujo OAuth PKCE con Spotify.
    Genera verifier, challenge y state. Guarda en pkce_sessions y redirige a Spotify.

    Returns:
        RedirectResponse: Redirige al usuario a la página de autorización de Spotify.
    """
    code_verifier, code_challenge = _generate_pkce()
    state = str(uuid.uuid4())

    # Guardar state → verifier en la base de datos
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO public.pkce_sessions (state, verifier) VALUES (%s, %s)",
                (state, code_verifier)
            )
        conn.commit()
    finally:
        conn.close()

    # Construir URL de autorización de Spotify
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": SCOPES,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state,
    }
    auth_url = f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url=auth_url)