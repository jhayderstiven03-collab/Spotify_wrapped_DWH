"""
filename: etl_service.py
author: Jhayder Florez
date: 2026-05-15
version: 1.0
description: ETL pipeline service. Orchestrates the three phases (Extract, Transform, Load)
             for all four Spotify endpoints into the DWH.
"""

import time
from datetime import datetime, timezone

from zoneinfo import ZoneInfo
from backend.app.core.database import get_connection
from backend.app.core.spotify_client import (
    get_user_profile,
    get_top_artists,
    get_top_tracks,
    get_recently_played,
)


# ─────────────────────────────────────────────
# EXTRACT
# ─────────────────────────────────────────────

def extract_user(token: str) -> dict:
    """
    Extracts raw user profile data from Spotify.

    Args:
        token (str): Spotify access token.

    Returns:
        dict: Raw user profile JSON from Spotify.
    """
    return get_user_profile(token)


def extract_top_artists(token: str) -> list[dict]:
    """
    Extracts raw top artists data from Spotify.

    Args:
        token (str): Spotify access token.

    Returns:
        list[dict]: Raw list of top artist objects from Spotify.
    """
    return get_top_artists(token)


def extract_top_tracks(token: str) -> list[dict]:
    """
    Extracts raw top tracks data from Spotify.

    Args:
        token (str): Spotify access token.

    Returns:
        list[dict]: Raw list of top track objects from Spotify.
    """
    return get_top_tracks(token)


def extract_recently_played(token: str, after_ms: int | None = None) -> list[dict]:
    """
    Extracts raw recently played history from Spotify.

    Args:
        token (str): Spotify access token.
        after_ms (int | None): Cursor in Unix ms. Only returns tracks after this moment.

    Returns:
        list[dict]: Raw list of PlayHistoryObject from Spotify.
    """
    return get_recently_played(token, after_ms)


# ─────────────────────────────────────────────
# TRANSFORM
# ─────────────────────────────────────────────

def transform_user(raw: dict) -> dict:
    """
    Normalizes raw Spotify user profile into a dwh.dim_users-ready dict.

    Args:
        raw (dict): Raw user profile JSON from Spotify.

    Returns:
        dict: Normalized user data matching dwh.dim_users columns.
    """
    return {
        "spotify_id":   raw["id"],
        "display_name": raw.get("display_name"),
        "email":        raw.get("email"),
        "country":      raw.get("country"),
        "followers":    raw.get("followers", {}).get("total", 0),
        "product":      raw.get("product"),
    }


def transform_artists(raw_list: list[dict]) -> list[dict]:
    """
    Normalizes a list of raw Spotify artist objects into dwh.dim_artists-ready dicts.

    Args:
        raw_list (list[dict]): Raw list of artist objects from Spotify.

    Returns:
        list[dict]: Normalized artist data matching dwh.dim_artists columns.
    """
    result = []
    for item in raw_list:
        result.append({
            "spotify_id":      item["id"],
            "name":            item["name"],
            "popularity":      item.get("popularity"),
            "followers_count": item.get("followers", {}).get("total", 0),
            "genres":          item.get("genres", []),
        })
    return result


def transform_tracks(raw_list: list[dict]) -> list[dict]:
    """
    Normalizes a list of raw Spotify track objects into dwh.dim_tracks-ready dicts.

    Args:
        raw_list (list[dict]): Raw list of track objects from Spotify.

    Returns:
        list[dict]: Normalized track data matching dwh.dim_tracks columns.
    """
    result = []
    for item in raw_list:
        result.append({
            "spotify_id":       item["id"],
            "name":             item["name"],
            "artist_spotify_id": item["artists"][0]["id"] if item.get("artists") else None,
            "album_name":       item.get("album", {}).get("name"),
            "duration_ms":      item.get("duration_ms"),
            "popularity":       item.get("popularity"),
            "explicit":         item.get("explicit", False),
        })
    return result


def transform_history(raw_list: list[dict]) -> list[dict]:
    """
    Normalizes a list of raw Spotify PlayHistoryObjects into
    dwh.fact_listening_history-ready dicts.
    Timestamps are converted from UTC to Colombia timezone (UTC-5).

    Args:
        raw_list (list[dict]): Raw list of PlayHistoryObject from Spotify.

    Returns:
        list[dict]: Normalized history data matching dwh.fact_listening_history columns.
    """
    COLOMBIA_TZ = ZoneInfo("America/Bogota")
    result = []
    for item in raw_list:
        played_at_str = item["played_at"]
        played_at_utc = datetime.fromisoformat(played_at_str.replace("Z", "+00:00"))
        played_at = played_at_utc.astimezone(COLOMBIA_TZ)
        track = item["track"]

        result.append({
            "track_spotify_id":  track["id"],
            "track_name":        track.get("name", "Unknown"),
            "artist_spotify_id": track["artists"][0]["id"] if track.get("artists") else None,
            "artist_name":       track["artists"][0]["name"] if track.get("artists") else None,
            "album_name":        track.get("album", {}).get("name"),
            "duration_ms":       track.get("duration_ms"),
            "popularity":        track.get("popularity"),
            "explicit":          track.get("explicit", False),
            "played_at":         played_at,
            "hour_of_day":       played_at.hour,
            "day_of_week":       played_at.strftime("%A"),
            "context_type":      (item.get("context") or {}).get("type") or "unknown",
        })
    return result
# ─────────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────────

def load_user(conn, user: dict) -> int:
    """
    Inserts or updates a user record in dwh.dim_users.

    Args:
        conn: Active psycopg2 connection.
        user (dict): Normalized user data from transform_user.

    Returns:
        int: Number of new records inserted (0 or 1).
    """
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO dwh.dim_users
                (spotify_id, display_name, email, country, followers, product)
            VALUES (%(spotify_id)s, %(display_name)s, %(email)s,
                    %(country)s, %(followers)s, %(product)s)
            ON CONFLICT (spotify_id) DO NOTHING
        """, user)
        return cur.rowcount


def load_artists(conn, artists: list[dict]) -> tuple[int, int]:
    """
    Inserts artist records into dwh.dim_artists, skipping duplicates.

    Args:
        conn: Active psycopg2 connection.
        artists (list[dict]): Normalized artist data from transform_artists.

    Returns:
        tuple[int, int]: (new_count, skipped_count)
    """
    new_count = 0
    skipped_count = 0

    with conn.cursor() as cur:
        for artist in artists:
            cur.execute("""
                INSERT INTO dwh.dim_artists
                    (spotify_id, name, popularity, followers_count, genres)
                VALUES (%(spotify_id)s, %(name)s, %(popularity)s,
                        %(followers_count)s, %(genres)s)
                ON CONFLICT (spotify_id) DO NOTHING
            """, artist)
            if cur.rowcount == 1:
                new_count += 1
            else:
                skipped_count += 1

    return new_count, skipped_count


def load_tracks(conn, tracks: list[dict]) -> tuple[int, int]:
    """
    Inserts track records into dwh.dim_tracks, resolving the artist FK.

    Args:
        conn: Active psycopg2 connection.
        tracks (list[dict]): Normalized track data from transform_tracks.

    Returns:
        tuple[int, int]: (new_count, skipped_count)
    """
    new_count = 0
    skipped_count = 0

    with conn.cursor() as cur:
        for track in tracks:
            # Resolver FK: buscar artist_id por spotify_id del artista
            artist_id = None
            if track["artist_spotify_id"]:
                cur.execute(
                    "SELECT artist_id FROM dwh.dim_artists WHERE spotify_id = %s",
                    (track["artist_spotify_id"],)
                )
                row = cur.fetchone()
                artist_id = row["artist_id"] if row else None

            cur.execute("""
                INSERT INTO dwh.dim_tracks
                    (spotify_id, name, artist_id, album_name,
                     duration_ms, popularity, explicit)
                VALUES (%(spotify_id)s, %(name)s, %(artist_id)s, %(album_name)s,
                        %(duration_ms)s, %(popularity)s, %(explicit)s)
                ON CONFLICT (spotify_id) DO NOTHING
            """, {**track, "artist_id": artist_id})

            if cur.rowcount == 1:
                new_count += 1
            else:
                skipped_count += 1

    return new_count, skipped_count


def load_history(conn, history: list[dict], user_id: int) -> tuple[int, int]:
    """
    Inserts listening history records into dwh.fact_listening_history.
    Also inserts missing tracks and artists into dim_tracks and dim_artists.

    Args:
        conn: Active psycopg2 connection.
        history (list[dict]): Normalized history data from transform_history.
        user_id (int): Internal user_id from dwh.dim_users.

    Returns:
        tuple[int, int]: (new_count, skipped_count)
    """
    new_count = 0
    skipped_count = 0

    with conn.cursor() as cur:
        for item in history:

            # 1. Asegurar que el artista existe en dim_artists
            cur.execute(
                "SELECT artist_id FROM dwh.dim_artists WHERE spotify_id = %s",
                (item["artist_spotify_id"],)
            )
            artist_row = cur.fetchone()

            if not artist_row:
                cur.execute("""
                    INSERT INTO dwh.dim_artists
                        (spotify_id, name, popularity, followers_count, genres)
                    VALUES (%s, %s, NULL, NULL, '{}')
                    ON CONFLICT (spotify_id) DO NOTHING
                    RETURNING artist_id
                """, (item["artist_spotify_id"], item["artist_name"]))
                artist_row = cur.fetchone()
                if not artist_row:
                    cur.execute(
                        "SELECT artist_id FROM dwh.dim_artists WHERE spotify_id = %s",
                        (item["artist_spotify_id"],)
                    )
                    artist_row = cur.fetchone()

            if not artist_row:
                skipped_count += 1
                continue

            artist_id = artist_row["artist_id"]

            # 2. Asegurar que el track existe en dim_tracks
            cur.execute(
                "SELECT track_id FROM dwh.dim_tracks WHERE spotify_id = %s",
                (item["track_spotify_id"],)
            )
            track_row = cur.fetchone()

            if not track_row:
                cur.execute("""
                    INSERT INTO dwh.dim_tracks
                        (spotify_id, name, artist_id, album_name,
                         duration_ms, popularity, explicit)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (spotify_id) DO NOTHING
                    RETURNING track_id
                """, (
                    item["track_spotify_id"],
                    item["track_name"],
                    artist_id,
                    item["album_name"],
                    item["duration_ms"],
                    item["popularity"],
                    item["explicit"],
                ))
                track_row = cur.fetchone()
                if not track_row:
                    cur.execute(
                        "SELECT track_id FROM dwh.dim_tracks WHERE spotify_id = %s",
                        (item["track_spotify_id"],)
                    )
                    track_row = cur.fetchone()

            if not track_row:
                skipped_count += 1
                continue

            track_id = track_row["track_id"]

            # 3. Insertar en fact_listening_history
            cur.execute("""
                INSERT INTO dwh.fact_listening_history
                    (user_id, track_id, artist_id, played_at,
                     hour_of_day, day_of_week, context_type)
                VALUES (%(user_id)s, %(track_id)s, %(artist_id)s, %(played_at)s,
                        %(hour_of_day)s, %(day_of_week)s, %(context_type)s)
                ON CONFLICT (user_id, played_at) DO NOTHING
            """, {
                **item,
                "user_id":   user_id,
                "track_id":  track_id,
                "artist_id": artist_id,
            })

            if cur.rowcount == 1:
                new_count += 1
            else:
                skipped_count += 1

    return new_count, skipped_count


# ─────────────────────────────────────────────
# AUDITORÍA
# ─────────────────────────────────────────────

def insert_audit_start(conn, spotify_user_id: str) -> int:
    """
    Inserts a new audit record with status 'running' at ETL start.

    Args:
        conn: Active psycopg2 connection.
        spotify_user_id (str): Spotify user ID of the authenticated user.

    Returns:
        int: audit_id of the new record.
    """
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO dwh.etl_audit (spotify_user_id, started_at, status)
            VALUES (%s, NOW(), 'running')
            RETURNING audit_id
        """, (spotify_user_id,))
        return cur.fetchone()["audit_id"]


def get_last_cursor(conn, spotify_user_id: str) -> int | None:
    """
    Retrieves the cursor_next_ms from the last successful ETL run.

    Args:
        conn: Active psycopg2 connection.
        spotify_user_id (str): Spotify user ID.

    Returns:
        int | None: Unix ms cursor, or None if no previous run exists.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT cursor_next_ms
            FROM dwh.etl_audit
            WHERE spotify_user_id = %s AND status = 'success'
            ORDER BY started_at DESC
            LIMIT 1
        """, (spotify_user_id,))
        row = cur.fetchone()
        return row["cursor_next_ms"] if row else None


def get_max_played_at_ms(conn, spotify_user_id: str) -> int | None:
    """
    Returns the MAX(played_at) from fact_listening_history as Unix ms.
    Used as cursor_next_ms for the next ETL run.

    Args:
        conn: Active psycopg2 connection.
        spotify_user_id (str): Spotify user ID.

    Returns:
        int | None: Unix ms of the latest played_at, or None if no records.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT MAX(f.played_at) as max_played_at
            FROM dwh.fact_listening_history f
            JOIN dwh.dim_users u ON u.user_id = f.user_id
            WHERE u.spotify_id = %s
        """, (spotify_user_id,))
        row = cur.fetchone()
        if row and row["max_played_at"]:
            return int(row["max_played_at"].timestamp() * 1000)
        return None


def update_audit_success(conn, audit_id: int, duration_ms: int,
                         cursor_after_ms: int | None, cursor_next_ms: int | None,
                         users_new: int, artists_new: int, artists_skipped: int,
                         tracks_new: int, tracks_skipped: int,
                         history_new: int, history_skipped: int) -> None:
    """
    Updates the audit record with success status and execution metrics.

    Args:
        conn: Active psycopg2 connection.
        audit_id (int): ID of the audit record to update.
        duration_ms (int): Total ETL duration in milliseconds.
        cursor_after_ms (int | None): Cursor used in this run.
        cursor_next_ms (int | None): Cursor for the next run.
        users_new (int): New user records inserted.
        artists_new (int): New artist records inserted.
        artists_skipped (int): Artist records skipped (already existed).
        tracks_new (int): New track records inserted.
        tracks_skipped (int): Track records skipped (already existed).
        history_new (int): New history records inserted.
        history_skipped (int): History records skipped (already existed).
    """
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE dwh.etl_audit SET
                finished_at      = NOW(),
                status           = 'success',
                duration_ms      = %(duration_ms)s,
                cursor_after_ms  = %(cursor_after_ms)s,
                cursor_next_ms   = %(cursor_next_ms)s,
                users_new        = %(users_new)s,
                artists_new      = %(artists_new)s,
                artists_skipped  = %(artists_skipped)s,
                tracks_new       = %(tracks_new)s,
                tracks_skipped   = %(tracks_skipped)s,
                history_new      = %(history_new)s,
                history_skipped  = %(history_skipped)s
            WHERE audit_id = %(audit_id)s
        """, {
            "audit_id":        audit_id,
            "duration_ms":     duration_ms,
            "cursor_after_ms": cursor_after_ms,
            "cursor_next_ms":  cursor_next_ms,
            "users_new":       users_new,
            "artists_new":     artists_new,
            "artists_skipped": artists_skipped,
            "tracks_new":      tracks_new,
            "tracks_skipped":  tracks_skipped,
            "history_new":     history_new,
            "history_skipped": history_skipped,
        })


def update_audit_error(conn, audit_id: int, duration_ms: int,
                       error_message: str) -> None:
    """
    Updates the audit record with error status and error message.

    Args:
        conn: Active psycopg2 connection.
        audit_id (int): ID of the audit record to update.
        duration_ms (int): Total duration until the error occurred.
        error_message (str): Error description.
    """
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE dwh.etl_audit SET
                finished_at   = NOW(),
                status        = 'error',
                duration_ms   = %(duration_ms)s,
                error_message = %(error_message)s
            WHERE audit_id = %(audit_id)s
        """, {
            "audit_id":      audit_id,
            "duration_ms":   duration_ms,
            "error_message": error_message,
        })


# ─────────────────────────────────────────────
# ORQUESTADOR PRINCIPAL
# ─────────────────────────────────────────────

def run_etl(spotify_token: str, spotify_user_id: str) -> dict:
    """
    Orchestrates the full ETL pipeline: Extract → Transform → Load.
    Records execution metrics in dwh.etl_audit.

    Args:
        spotify_token (str): Valid Spotify access token.
        spotify_user_id (str): Spotify user ID of the authenticated user.

    Returns:
        dict: Execution summary with metrics and step log.
    """
    conn = get_connection()
    steps = []
    t0 = time.time()

    conn.autocommit = False
    audit_id = insert_audit_start(conn, spotify_user_id)
    conn.commit()

    try:
        # ── Obtener cursor de la última ejecución ──
        cursor_after_ms = get_last_cursor(conn, spotify_user_id)
        steps.append({"phase": "Setup", "detail": f"Cursor from last run: {cursor_after_ms}", "ok": True})

        # ── EXTRACT ──
        raw_user    = extract_user(spotify_token)
        steps.append({"phase": "Extract", "detail": "User profile fetched", "ok": True})

        raw_artists = extract_top_artists(spotify_token)
        steps.append({"phase": "Extract", "detail": f"{len(raw_artists)} artists fetched", "ok": True})

        raw_tracks  = extract_top_tracks(spotify_token)
        steps.append({"phase": "Extract", "detail": f"{len(raw_tracks)} tracks fetched", "ok": True})

        raw_history = extract_recently_played(spotify_token, cursor_after_ms)
        steps.append({"phase": "Extract", "detail": f"{len(raw_history)} history items fetched", "ok": True})

        # ── TRANSFORM ──
        user    = transform_user(raw_user)
        artists = transform_artists(raw_artists)
        tracks  = transform_tracks(raw_tracks)
        history = transform_history(raw_history)
        steps.append({"phase": "Transform", "detail": "All data normalized", "ok": True})

        # ── LOAD ──
        users_new                      = load_user(conn, user)
        steps.append({"phase": "Load", "detail": f"dim_users — {users_new} new", "ok": True})

        artists_new, artists_skipped   = load_artists(conn, artists)
        steps.append({"phase": "Load", "detail": f"dim_artists — {artists_new} new / {artists_skipped} skipped", "ok": True})

        tracks_new, tracks_skipped     = load_tracks(conn, tracks)
        steps.append({"phase": "Load", "detail": f"dim_tracks — {tracks_new} new / {tracks_skipped} skipped", "ok": True})

        # Obtener user_id interno para fact_listening_history
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id FROM dwh.dim_users WHERE spotify_id = %s",
                (spotify_user_id,)
            )
            user_id = cur.fetchone()["user_id"]


        # Cargar en dim_tracks las canciones del historial que no estén aún
        for item in history:
            track = item  # ya viene transformado
            with conn.cursor() as cur:
                # Verificar si ya existe
                cur.execute(
                    "SELECT track_id FROM dwh.dim_tracks WHERE spotify_id = %s",
                    (track["track_spotify_id"],)
                )
                if not cur.fetchone():
                    # Buscar el artista
                    cur.execute(
                        "SELECT artist_id FROM dwh.dim_artists WHERE spotify_id = %s",
                        (track["artist_spotify_id"],)
                    )
                    artist_row = cur.fetchone()
                    artist_id = artist_row["artist_id"] if artist_row else None

                    cur.execute("""
                        INSERT INTO dwh.dim_tracks
                            (spotify_id, name, artist_id, album_name,
                            duration_ms, popularity, explicit)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (spotify_id) DO NOTHING
                    """, (
                        track["track_spotify_id"],
                        item.get("track_name", "Unknown"),
                        artist_id,
                        None,
                        None,
                        None,
                        None,
                    ))
        

        history_new, history_skipped   = load_history(conn, history, user_id)
        steps.append({"phase": "Load", "detail": f"fact_listening_history — {history_new} new / {history_skipped} skipped", "ok": True})

        # ── AUDITORÍA ──
        cursor_next_ms = get_max_played_at_ms(conn, spotify_user_id)
        duration_ms    = int((time.time() - t0) * 1000)

        update_audit_success(
            conn, audit_id, duration_ms,
            cursor_after_ms, cursor_next_ms,
            users_new, artists_new, artists_skipped,
            tracks_new, tracks_skipped,
            history_new, history_skipped
        )
        conn.commit()
        steps.append({"phase": "Audit", "detail": f"Recorded — duration: {duration_ms}ms", "ok": True})

        return {
            "audit_id":    audit_id,
            "duration_ms": duration_ms,
            "status":      "success",
            "steps":       steps,
            "metrics": {
                "users_new":        users_new,
                "artists_new":      artists_new,
                "artists_skipped":  artists_skipped,
                "tracks_new":       tracks_new,
                "tracks_skipped":   tracks_skipped,
                "history_new":      history_new,
                "history_skipped":  history_skipped,
            }
        }

    except Exception as e:
        conn.rollback()
        duration_ms = int((time.time() - t0) * 1000)
        steps.append({"phase": "Error", "detail": str(e), "ok": False})
        update_audit_error(conn, audit_id, duration_ms, str(e))
        conn.commit()
        raise

    finally:
        conn.close()