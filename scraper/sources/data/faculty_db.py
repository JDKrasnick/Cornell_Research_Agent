"""Database operations for faculty storage."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .connection import get_db_connection


@dataclass
class Faculty:
    """Represents a faculty member."""
    id: Optional[int]
    name: str
    website_url: Optional[str]
    email: Optional[str]
    department: Optional[str]
    profile_url: Optional[str]
    research_interests: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


def drop_faculty_table(conn: sqlite3.Connection) -> None:
    """Drop the faculty table if it exists."""
    conn.execute("DROP TABLE IF EXISTS faculty")
    conn.commit()


def init_faculty_table(conn: sqlite3.Connection) -> None:
    """Create the faculty table if it doesn't exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            website_url TEXT,
            email TEXT,
            department TEXT,
            profile_url TEXT,
            research_interests TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_faculty_name
        ON faculty(name)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_faculty_department
        ON faculty(department)
    """)
    conn.commit()


def store_faculty(conn: sqlite3.Connection, faculty_list: List[dict]) -> int:
    """
    Store faculty members in the database.

    Args:
        conn: Database connection
        faculty_list: List of faculty dicts with name, website, email, etc.

    Returns:
        Number of faculty inserted/updated
    """
    cursor = conn.cursor()
    count = 0
    now = datetime.now().isoformat()

    for f in faculty_list:
        cursor.execute("""
            INSERT INTO faculty (
                name, website_url, email, department, profile_url, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                website_url = COALESCE(excluded.website_url, faculty.website_url),
                email = COALESCE(excluded.email, faculty.email),
                department = COALESCE(excluded.department, faculty.department),
                profile_url = COALESCE(excluded.profile_url, faculty.profile_url),
                updated_at = excluded.updated_at
        """, (
            f.get("name"),
            f.get("website"),
            f.get("email"),
            f.get("department"),
            f.get("profile_url"),
            now
        ))
        count += 1

    conn.commit()
    return count


def get_all_faculty(conn: sqlite3.Connection) -> List[Faculty]:
    """Retrieve all faculty members from the database."""
    cursor = conn.execute("""
        SELECT id, name, website_url, email, department, profile_url,
               research_interests, created_at, updated_at
        FROM faculty
        ORDER BY name
    """)

    rows = cursor.fetchall()
    return [
        Faculty(
            id=row[0],
            name=row[1],
            website_url=row[2],
            email=row[3],
            department=row[4],
            profile_url=row[5],
            research_interests=row[6],
            created_at=datetime.fromisoformat(row[7]) if row[7] else None,
            updated_at=datetime.fromisoformat(row[8]) if row[8] else None
        )
        for row in rows
    ]


def get_faculty_by_name(conn: sqlite3.Connection, name: str) -> Optional[Faculty]:
    """Retrieve a faculty member by name."""
    cursor = conn.execute("""
        SELECT id, name, website_url, email, department, profile_url,
               research_interests, created_at, updated_at
        FROM faculty
        WHERE name = ?
    """, (name,))

    row = cursor.fetchone()
    if not row:
        return None

    return Faculty(
        id=row[0],
        name=row[1],
        website_url=row[2],
        email=row[3],
        department=row[4],
        profile_url=row[5],
        research_interests=row[6],
        created_at=datetime.fromisoformat(row[7]) if row[7] else None,
        updated_at=datetime.fromisoformat(row[8]) if row[8] else None
    )


def update_research_interests(
    conn: sqlite3.Connection, name: str, research_interests: str
) -> bool:
    """
    Update the research_interests field for a faculty member.

    Args:
        conn: Database connection
        name: Faculty member name
        research_interests: Comma-separated research interests string

    Returns:
        True if a row was updated, False if faculty not found
    """
    now = datetime.now().isoformat()
    cursor = conn.execute("""
        UPDATE faculty
        SET research_interests = ?, updated_at = ?
        WHERE name = ?
    """, (research_interests, now, name))
    conn.commit()
    return cursor.rowcount > 0


def get_faculty_by_department(conn: sqlite3.Connection, department: str) -> List[Faculty]:
    """Retrieve all faculty members in a department."""
    cursor = conn.execute("""
        SELECT id, name, website_url, email, department, profile_url,
               research_interests, created_at, updated_at
        FROM faculty
        WHERE department = ?
        ORDER BY name
    """, (department,))

    rows = cursor.fetchall()
    return [
        Faculty(
            id=row[0],
            name=row[1],
            website_url=row[2],
            email=row[3],
            department=row[4],
            profile_url=row[5],
            research_interests=row[6],
            created_at=datetime.fromisoformat(row[7]) if row[7] else None,
            updated_at=datetime.fromisoformat(row[8]) if row[8] else None
        )
        for row in rows
    ]