"""
filename: security.py
author: Jhayder Florez
date: 2026-05-13
version: 1.0
description: Dependency de FastAPI para validar el JWT de la app y extraer el spotify_id del usuario autenticado.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from backend.app.core.config import settings

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> str:
    """
    Valida el JWT enviado en el header Authorization y retorna el spotify_id.

    Args:
        credentials: Header Authorization con el token Bearer.

    Returns:
        str: spotify_id del usuario autenticado.

    Raises:
        HTTPException 401: si el token es inválido, expirado o no contiene 'sub'.
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        spotify_id: str = payload.get("sub")
        if spotify_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: falta el campo sub"
            )
        return spotify_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )