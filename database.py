import sqlite3
from typing import List, Dict, Any
from config import DB_PATH, logger

def get_connection():
    """Create a database connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with the required tables."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS magic_sets (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    release_date TEXT NOT NULL,
                    wallpaper_downloaded BOOLEAN NOT NULL DEFAULT 0,
                    gcal_created BOOLEAN NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

def add_or_update_sets(sets_data: List[Dict[str, Any]]):
    """
    Insert or update a list of sets in the database.
    sets_data should be a list of dicts with 'code', 'name', 'released_at'.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            for s in sets_data:
                cursor.execute('''
                    INSERT INTO magic_sets (code, name, release_date) 
                    VALUES (?, ?, ?)
                    ON CONFLICT(code) DO UPDATE SET
                    name=excluded.name,
                    release_date=excluded.release_date
                ''', (s['code'], s['name'], s['released_at']))
            conn.commit()
            logger.info(f"Added/Updated {len(sets_data)} sets in the database.")
    except Exception as e:
        logger.error(f"Error saving sets: {e}")

def get_pending_wallpapers() -> List[Dict[str, Any]]:
    """Retrieve all sets that don't have a wallpaper downloaded yet."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT code, name, release_date FROM magic_sets WHERE wallpaper_downloaded = 0")
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error fetching pending wallpapers: {e}")
        return []

def get_pending_gcal() -> List[Dict[str, Any]]:
    """Retrieve all sets that don't have a calendar event generated yet."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT code, name, release_date FROM magic_sets WHERE gcal_created = 0")
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error fetching pending Google Calendar events: {e}")
        return []

def mark_wallpaper_done(code: str):
    """Mark wallpaper as downloaded for a set."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE magic_sets SET wallpaper_downloaded = 1 WHERE code = ?", (code,))
            conn.commit()
            logger.info(f"Marked wallpaper as downloaded for set {code}.")
    except Exception as e:
        logger.error(f"Error updating wallpaper status for {code}: {e}")

def mark_gcal_done(code: str):
    """Mark Google Calendar event as created for a set."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE magic_sets SET gcal_created = 1 WHERE code = ?", (code,))
            conn.commit()
            logger.info(f"Marked Google Calendar event as created for set {code}.")
    except Exception as e:
        logger.error(f"Error updating calendar status for {code}: {e}")
