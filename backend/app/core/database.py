"""
filename: database.py
author: CAMILO TORRES
date: 2026-05-13
version: 1.0
description: Configuración de la conexión a PostgreSQL en Neon usando psycopg2.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from backend.app.core.config import settings


def get_connection():
    """
    Abre y retorna una conexión directa a PostgreSQL en Neon.

    Returns:
        connection: Conexión psycopg2 activa.
    """
    return psycopg2.connect(settings.DATABASE_URL, cursor_factory=RealDictCursor)