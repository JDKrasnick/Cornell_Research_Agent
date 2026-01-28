"""Database operations for publications storage."""

import sqlite3
from datetime import datetime
from typing import List

from .models import Publication


def init_publications_table(conn: sqlite3.Connection) -> None:
    """Create the publications table if it doesn't exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS publications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id TEXT NOT NULL,
            title TEXT NOT NULL,
            abstract TEXT,
            citation_count INTEGER DEFAULT 0,
            year INTEGER,
            venue TEXT,
            url TEXT,
            professor_name TEXT NOT NULL,
            author_id TEXT NOT NULL,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(paper_id, professor_name)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_publications_professor
        ON publications(professor_name)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_publications_citations
        ON publications(citation_count DESC)
    """)
    conn.commit()


def store_publications(conn: sqlite3.Connection, publications: List[Publication]) -> int:
    """
    Store publications in the database.

    Args:
        conn: Database connection
        publications: List of Publication objects to store

    Returns:
        Number of publications inserted/updated
    """
    cursor = conn.cursor()
    count = 0

    for pub in publications:
        cursor.execute("""
            INSERT INTO publications (
                paper_id, title, abstract, citation_count, year,
                venue, url, professor_name, author_id, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(paper_id, professor_name) DO UPDATE SET
                title = excluded.title,
                abstract = excluded.abstract,
                citation_count = excluded.citation_count,
                year = excluded.year,
                venue = excluded.venue,
                url = excluded.url,
                fetched_at = excluded.fetched_at
        """, (
            pub.paper_id,
            pub.title,
            pub.abstract,
            pub.citation_count,
            pub.year,
            pub.venue,
            pub.url,
            pub.professor_name,
            pub.author_id,
            pub.fetched_at.isoformat()
        ))
        count += 1

    conn.commit()
    return count


def get_publications_for_professor(
    conn: sqlite3.Connection,
    professor_name: str
) -> List[Publication]:
    """
    Retrieve all stored publications for a professor.

    Args:
        conn: Database connection
        professor_name: Name of the professor

    Returns:
        List of Publication objects sorted by citation count (descending)
    """
    cursor = conn.execute("""
        SELECT * FROM publications
        WHERE professor_name = ?
        ORDER BY citation_count DESC
    """, (professor_name,))

    rows = cursor.fetchall()
    return [
        Publication(
            paper_id=row["paper_id"],
            title=row["title"],
            abstract=row["abstract"],
            citation_count=row["citation_count"],
            year=row["year"],
            venue=row["venue"],
            url=row["url"],
            professor_name=row["professor_name"],
            author_id=row["author_id"],
            fetched_at=datetime.fromisoformat(row["fetched_at"])
        )
        for row in rows
    ]