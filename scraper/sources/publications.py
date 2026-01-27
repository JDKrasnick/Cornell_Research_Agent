"""
Fetch top publications from Semantic Scholar and store in SQLite database.

This module provides functions to search for a professor's publications
using the Semantic Scholar API and store them in a local SQLite database.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import requests

from config.settings import settings
from .data import (
    Publication,
    get_db_connection,
    init_publications_table,
    store_publications,
    get_publications_for_professor,
)

logger = logging.getLogger(__name__)

SEMANTIC_SCHOLAR_SEARCH_API = "https://api.semanticscholar.org/graph/v1/author/search"
SEMANTIC_SCHOLAR_AUTHOR_PAPERS_API = "https://api.semanticscholar.org/graph/v1/author/{author_id}/papers"


def fetch_top_publications(
    professor_name: str,
    top_n: int = 10,
    api_key: Optional[str] = None
) -> Tuple[List[Publication], Optional[str]]:
    """
    Fetch the top N most cited publications for a professor from Semantic Scholar.

    Args:
        professor_name: Name of the professor to search for
        top_n: Number of top publications to return (default 10)
        api_key: Optional Semantic Scholar API key for higher rate limits

    Returns:
        Tuple of (list of Publication objects, error message if any)
    """
    headers = {}
    if api_key or settings.semantic_scholar_api_key:
        headers["x-api-key"] = api_key or settings.semantic_scholar_api_key

    try:
        # Search for the author
        search_resp = requests.get(
            SEMANTIC_SCHOLAR_SEARCH_API,
            params={"query": professor_name, "fields": "name,authorId"},
            headers=headers,
            timeout=30
        )
        search_resp.raise_for_status()
        search_data = search_resp.json()

        if not search_data.get("data"):
            return [], f"Author '{professor_name}' not found on Semantic Scholar"

        author = search_data["data"][0]
        author_id = author["authorId"]

        # Fetch papers with detailed fields
        papers_resp = requests.get(
            SEMANTIC_SCHOLAR_AUTHOR_PAPERS_API.format(author_id=author_id),
            params={
                "fields": "paperId,title,abstract,citationCount,year,venue,url",
                "limit": 100  # Fetch more to ensure we get enough with citation data
            },
            headers=headers,
            timeout=30
        )
        papers_resp.raise_for_status()
        papers_data = papers_resp.json()

        papers = papers_data.get("data", [])
        if not papers:
            return [], f"No papers found for author '{professor_name}'"

        # Sort by citation count and take top N
        sorted_papers = sorted(
            papers,
            key=lambda p: p.get("citationCount") or 0,
            reverse=True
        )[:top_n]

        fetched_at = datetime.now()
        publications = [
            Publication(
                paper_id=paper.get("paperId", ""),
                title=paper.get("title", "Untitled"),
                abstract=paper.get("abstract"),
                citation_count=paper.get("citationCount") or 0,
                year=paper.get("year"),
                venue=paper.get("venue"),
                url=paper.get("url"),
                professor_name=professor_name,
                author_id=author_id,
                fetched_at=fetched_at
            )
            for paper in sorted_papers
        ]

        return publications, None

    except requests.exceptions.Timeout:
        return [], "Request timed out while fetching publications"
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return [], "Rate limit exceeded. Try again later or use an API key."
        return [], f"HTTP error: {e.response.status_code}"
    except requests.exceptions.RequestException as e:
        return [], f"Network error: {str(e)}"
    except Exception as e:
        logger.exception("Unexpected error fetching publications")
        return [], f"Unexpected error: {str(e)}"


def scrape_and_store_publications(
    professor_name: str,
    top_n: int = 10,
    db_path: Optional[Path] = None
) -> Tuple[int, Optional[str]]:
    """
    Fetch top publications for a professor and store them in the database.

    Args:
        professor_name: Name of the professor
        top_n: Number of top publications to fetch (default 10)
        db_path: Optional custom database path

    Returns:
        Tuple of (number of publications stored, error message if any)
    """
    publications, error = fetch_top_publications(professor_name, top_n)

    if error:
        return 0, error

    if not publications:
        return 0, None

    conn = get_db_connection(db_path)
    try:
        init_publications_table(conn)
        count = store_publications(conn, publications)
        logger.info(f"Stored {count} publications for {professor_name}")
        return count, None
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m scraper.sources.publications <professor_name>")
        sys.exit(1)

    professor_name = " ".join(sys.argv[1:])
    print(f"Fetching top 10 publications for: {professor_name}")

    count, error = scrape_and_store_publications(professor_name)

    if error:
        print(f"Error: {error}")
        sys.exit(1)

    print(f"Successfully stored {count} publications")

    # Display stored publications
    conn = get_db_connection()
    init_publications_table(conn)
    publications = get_publications_for_professor(conn, professor_name)
    conn.close()

    print(f"\n{'='*60}")
    print(f"Top {len(publications)} Publications for {professor_name}")
    print(f"{'='*60}")

    for i, pub in enumerate(publications, 1):
        print(f"\n{i}. {pub.title}")
        print(f"   Citations: {pub.citation_count}")
        if pub.year:
            print(f"   Year: {pub.year}")
        if pub.venue:
            print(f"   Venue: {pub.venue}")
        if pub.url:
            print(f"   URL: {pub.url}")