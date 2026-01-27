"""Database connection management for the scraper."""

import sqlite3
from pathlib import Path
from typing import Optional

from config.settings import settings


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Get a connection to the SQLite database.

    Args:
        db_path: Optional custom database path. Uses settings.database_path if not provided.

    Returns:
        SQLite connection with Row factory enabled.
    """
    if db_path is None:
        db_path = settings.database_path

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_database(db_path: Optional[Path] = None) -> None:
    """
    Initialize all database tables.

    Args:
        db_path: Optional custom database path.
    """
    from .publications_db import init_publications_table

    conn = get_db_connection(db_path)
    try:
        init_publications_table(conn)
    finally:
        conn.close()