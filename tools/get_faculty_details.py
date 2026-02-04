"""Lookup full profile by ID."""

from typing import Optional, Dict, Any

from scraper.sources.data import get_db_connection, get_faculty_by_name
from scraper.sources.data.publications_db import get_publications_for_professor


def get_faculty_details(
    faculty_id: Optional[int] = None,
    faculty_name: Optional[str] = None,
    include_publications: bool = True,
    max_publications: int = 10
) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a faculty member.

    Args:
        faculty_id: Database ID of the faculty member
        faculty_name: Name of the faculty member (alternative to ID)
        include_publications: Whether to include publications in the result
        max_publications: Maximum number of publications to return

    Returns:
        Dictionary with faculty details or None if not found
    """
    if not faculty_id and not faculty_name:
        raise ValueError("Either faculty_id or faculty_name must be provided")

    conn = get_db_connection()
    try:
        # Fetch faculty by name or ID
        if faculty_name:
            faculty = get_faculty_by_name(conn, faculty_name)
        else:
            # Query by ID
            cursor = conn.execute("""
                SELECT id, name, website_url, email, department, profile_url,
                       research_interests, created_at, updated_at
                FROM faculty
                WHERE id = ?
            """, (faculty_id,))
            row = cursor.fetchone()

            if not row:
                return None

            from scraper.sources.data.faculty_db import Faculty
            from datetime import datetime

            faculty = Faculty(
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

        if not faculty:
            return None

        # Build result dictionary
        result = {
            'id': faculty.id,
            'name': faculty.name,
            'email': faculty.email,
            'website_url': faculty.website_url,
            'profile_url': faculty.profile_url,
            'department': faculty.department,
            'research_interests': faculty.research_interests,
            'created_at': faculty.created_at.isoformat() if faculty.created_at else None,
            'updated_at': faculty.updated_at.isoformat() if faculty.updated_at else None
        }

        # Add publications if requested
        if include_publications:
            publications = get_publications_for_professor(conn, faculty.name)

            # Limit and format publications
            pub_list = []
            for pub in publications[:max_publications]:
                pub_list.append({
                    'paper_id': pub.paper_id,
                    'title': pub.title,
                    'abstract': pub.abstract,
                    'citation_count': pub.citation_count,
                    'year': pub.year,
                    'venue': pub.venue,
                    'url': pub.url
                })

            result['publications'] = pub_list
            result['total_publications'] = len(publications)

        return result

    finally:
        conn.close()