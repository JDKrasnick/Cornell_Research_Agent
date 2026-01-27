"""Data storage module for scraped research information."""

from .connection import get_db_connection, init_database
from .models import Publication
from .publications_db import (
    init_publications_table,
    store_publications,
    get_publications_for_professor,
)

__all__ = [
    "get_db_connection",
    "init_database",
    "Publication",
    "init_publications_table",
    "store_publications",
    "get_publications_for_professor",
]