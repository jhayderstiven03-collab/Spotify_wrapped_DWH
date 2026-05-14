"""
filename: api.py
author: CAMILO TORRES
date: 2026-05-13
version: 1.0
description: Agrupa todos los routers de la versión 1 de la API.
"""

from fastapi import APIRouter
from backend.app.v1.routers import auth

router = APIRouter()
router.include_router(auth.router)