"""
filename: main.py
author: CAMILO TORRES
date: 2026-05-13
version: 1.0
description: Punto de entrada de la aplicación FastAPI. Configura CORS e incluye los routers de v1.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.v1.api import router as v1_router
from backend.app.core.config import settings

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/v1")