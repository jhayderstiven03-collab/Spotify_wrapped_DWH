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



@router.get("/callback")
def spotify_callback(code: str, state: str):
    """
    Recibe el código de autorización de Spotify, valida el state,
    intercambia el code por tokens, guarda en dim_users y emite el JWT de la app.

    Args:
        code (str): Código de autorización enviado por Spotify.
        state (str): UUID generado en /login para verificar la sesión PKCE.

    Returns:
        RedirectResponse: Redirige al frontend con el JWT en la URL.
    """
    conn = get_connection()
    try:
        # 1. Validar state y obtener verifier
        with conn.cursor() as cur:
            cur.execute(
                "SELECT verifier FROM public.pkce_sessions WHERE state = %s",
                (state,)
            )
            row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=400, detail="State inválido o expirado")

        code_verifier = row["verifier"]

        # 2. Eliminar la sesión PKCE (uso único)
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM public.pkce_sessions WHERE state = %s",
                (state,)
            )
        conn.commit()

        # 3. Intercambiar code por tokens de Spotify
        token_response = requests.post(
            SPOTIFY_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
                "client_id": settings.SPOTIFY_CLIENT_ID,
                "code_verifier": code_verifier,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Error al obtener tokens de Spotify")

        token_data = token_response.json()
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        expires_in = token_data["expires_in"]  # segundos (normalmente 3600)
        token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # 4. Obtener perfil del usuario desde Spotify
        profile_response = requests.get(
            SPOTIFY_ME_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if profile_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Error al obtener perfil de Spotify")

        profile = profile_response.json()
        spotify_id = profile["id"]

        # 5. UPSERT en dim_users
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO dwh.dim_users
                    (spotify_id, display_name, email, country, followers, product,
                     spotify_access_token, spotify_refresh_token, token_expires_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (spotify_id) DO UPDATE SET
                    display_name          = EXCLUDED.display_name,
                    email                 = EXCLUDED.email,
                    country               = EXCLUDED.country,
                    followers             = EXCLUDED.followers,
                    product               = EXCLUDED.product,
                    spotify_access_token  = EXCLUDED.spotify_access_token,
                    spotify_refresh_token = EXCLUDED.spotify_refresh_token,
                    token_expires_at      = EXCLUDED.token_expires_at
            """, (
                spotify_id,
                profile.get("display_name"),
                profile.get("email"),
                profile.get("country"),
                profile.get("followers", {}).get("total", 0),
                profile.get("product"),
                access_token,
                refresh_token,
                token_expires_at,
            ))
        conn.commit()

        # 6. Emitir JWT de la app
        app_token = _generate_app_jwt(spotify_id)

        # 7. Redirigir al frontend con el token en la URL
        frontend_callback = f"{settings.FRONTEND_URL}/callback?token={app_token}"
        return RedirectResponse(url=frontend_callback)

    finally:
        conn.close()


def _generate_app_jwt(spotify_id: str) -> str:
    """
    Genera un JWT firmado con la SECRET_KEY de la app.

    Args:
        spotify_id (str): ID de Spotify del usuario autenticado.

    Returns:
        str: JWT codificado con expiración de 8 horas.
    """
    payload = {
        "sub": spotify_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=8)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")