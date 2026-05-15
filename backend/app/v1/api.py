"""
filename: api.py
author: CAMILO TORRES
date: 2026-05-14
version: 1.0
description: Registers all v1 routers into the main API router.
"""

from fastapi import APIRouter
from backend.app.v1.routers import auth, profile, artists, tracks, history

router = APIRouter()
router.include_router(auth.router)
router.include_router(profile.router)
router.include_router(artists.router)
router.include_router(tracks.router)
router.include_router(history.router)