"""
filename: config.py
author: Jhayder Florez
date: 2026-05-13
version: 1.0
description: Configuración central de variables de entorno usando pydantic-settings.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    # Spotify
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    SPOTIFY_REDIRECT_URI: str

    # Base de datos
    DATABASE_URL: str

    # App
    APP_NAME: str = "Spotify DWH API"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str
    FRONTEND_URL: str


settings = Settings()