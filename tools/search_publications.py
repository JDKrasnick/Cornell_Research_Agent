"""Semantic Scholar / arXiv API wrapper with local database fallback."""

from typing import List, Dict, Any, Optional
import sqlite3

import httpx

from config.settings import settings
from scraper.sources.data import get_db_connection


class PublicationSearchTool:
    """Tool for searching academic publications via local DB and Semantic Scholar API."""

    SEMANTIC_SCHOLAR_BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: Optional[str] = None, use_local_db: bool = True):
        """
        Initialize the publication search tool.

        Args:
            api_key: Semantic Scholar API key (optional but recommended)
            use_local_db: Whether to search local database first
        """
        self.api_key = api_key or settings.semantic_scholar_api_key
        self.use_local_db = use_local_db
        self.headers = {}
        if self.api_key:
            self.headers["x-api-key"] = self.api_key

    def search_local_publications(
        self,
        query: Optional[str] = None,
        professor_name: Optional[str] = None,
        year: Optional[int] = None,
        min_citations: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search publications in the local database.

        Args:
            query: Search query for title/abstract (case-insensitive)
            professor_name: Filter by professor name
            year: Filter by publication year
            min_citations: Minimum citation count
            limit: Maximum number of results

        Returns:
            List of publication dictionaries
        """
        conn = get_db_connection()
        try:
            # Build query
            sql_parts = ["SELECT * FROM publications WHERE 1=1"]
            params = []

            if query:
                sql_parts.append("AND (LOWER(title) LIKE ? OR LOWER(abstract) LIKE ?)")
                query_pattern = f"%{query.lower()}%"
                params.extend([query_pattern, query_pattern])

            if professor_name:
                sql_parts.append("AND professor_name = ?")
                params.append(professor_name)

            if year:
                sql_parts.append("AND year = ?")
                params.append(year)

            if min_citations > 0:
                sql_parts.append("AND citation_count >= ?")
                params.append(min_citations)

            sql_parts.append("ORDER BY citation_count DESC, year DESC")
            sql_parts.append("LIMIT ?")
            params.append(limit)

            sql = " ".join(sql_parts)
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append({
                    'paperId': row['paper_id'],
                    'title': row['title'],
                    'abstract': row['abstract'],
                    'citationCount': row['citation_count'],
                    'year': row['year'],
                    'venue': row['venue'],
                    'url': row['url'],
                    'professor_name': row['professor_name'],
                    'author_id': row['author_id'],
                    'source': 'local_db'
                })

            return results

        finally:
            conn.close()

    def get_professor_publications_local(
        self,
        professor_name: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all publications for a professor from local database.

        Args:
            professor_name: Name of the professor
            limit: Maximum number of results

        Returns:
            List of publication dictionaries
        """
        return self.search_local_publications(
            professor_name=professor_name,
            limit=limit
        )

    def search_by_keywords_local(
        self,
        keywords: List[str],
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search publications by keywords in local database.

        Args:
            keywords: List of keywords to search for
            limit: Maximum number of results

        Returns:
            List of publication dictionaries
        """
        conn = get_db_connection()
        try:
            # Build OR query for keywords
            keyword_conditions = []
            params = []

            for keyword in keywords:
                keyword_conditions.append("(LOWER(title) LIKE ? OR LOWER(abstract) LIKE ?)")
                pattern = f"%{keyword.lower()}%"
                params.extend([pattern, pattern])

            sql = f"""
                SELECT * FROM publications
                WHERE {' OR '.join(keyword_conditions)}
                ORDER BY citation_count DESC, year DESC
                LIMIT ?
            """
            params.append(limit)

            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append({
                    'paperId': row['paper_id'],
                    'title': row['title'],
                    'abstract': row['abstract'],
                    'citationCount': row['citation_count'],
                    'year': row['year'],
                    'venue': row['venue'],
                    'url': row['url'],
                    'professor_name': row['professor_name'],
                    'source': 'local_db'
                })

            return results

        finally:
            conn.close()

    def search_papers(
        self,
        query: str,
        limit: int = 10,
        fields: Optional[List[str]] = None,
        year: Optional[str] = None,
        use_api_fallback: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for papers by keyword query.
        Searches local database first, then falls back to API if needed.

        Args:
            query: Search query string
            limit: Maximum number of results (max 100)
            fields: List of fields to include in response
            year: Year filter (e.g., "2023" or "2020-2023")
            use_api_fallback: Whether to use API if local results insufficient

        Returns:
            List of paper dictionaries
        """
        results = []

        # Try local database first
        if self.use_local_db:
            try:
                year_int = None
                if year and '-' not in year:
                    year_int = int(year)

                local_results = self.search_local_publications(
                    query=query,
                    year=year_int,
                    limit=limit
                )
                results.extend(local_results)
            except Exception as e:
                pass  # Fall through to API

        # If we have enough results or API fallback is disabled, return
        if len(results) >= limit or not use_api_fallback:
            return results[:limit]

        # Fall back to API for additional results
        if fields is None:
            fields = [
                "paperId", "title", "abstract", "year", "citationCount",
                "venue", "authors", "externalIds", "url"
            ]

        url = f"{self.SEMANTIC_SCHOLAR_BASE_URL}/paper/search"
        params = {
            "query": query,
            "limit": min(limit - len(results), 100),
            "fields": ",".join(fields)
        }

        if year:
            params["year"] = year

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                api_results = data.get("data", [])
                for paper in api_results:
                    paper['source'] = 'api'
                results.extend(api_results)

        except httpx.HTTPError as e:
            pass  # Return what we have

        return results[:limit]

    def get_author_papers(
        self,
        author_id: str,
        limit: int = 50,
        fields: Optional[List[str]] = None,
        author_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get papers by a specific author.
        Tries local database first if author_name provided.

        Args:
            author_id: Semantic Scholar author ID
            limit: Maximum number of papers to return
            fields: List of fields to include in response
            author_name: Optional author name for local DB lookup

        Returns:
            List of paper dictionaries
        """
        results = []

        # Try local database first if we have the author name
        if self.use_local_db and author_name:
            try:
                local_results = self.get_professor_publications_local(
                    professor_name=author_name,
                    limit=limit
                )
                results.extend(local_results)

                # If we have enough local results, return them
                if len(results) >= limit:
                    return results[:limit]
            except Exception as e:
                pass  # Fall through to API

        # Fall back to API
        if fields is None:
            fields = [
                "paperId", "title", "abstract", "year", "citationCount",
                "venue", "externalIds", "url"
            ]

        url = f"{self.SEMANTIC_SCHOLAR_BASE_URL}/author/{author_id}/papers"
        params = {
            "limit": min(limit - len(results), 1000),
            "fields": ",".join(fields)
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                api_results = data.get("data", [])
                for paper in api_results:
                    paper['source'] = 'api'
                results.extend(api_results)

        except httpx.HTTPError as e:
            pass  # Return what we have

        return results[:limit]

    def search_author(self, author_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for an author by name.

        Args:
            author_name: Name of the author

        Returns:
            Author information dict or None if not found
        """
        url = f"{self.SEMANTIC_SCHOLAR_BASE_URL}/author/search"
        params = {
            "query": author_name,
            "limit": 1,
            "fields": "authorId,name,paperCount,citationCount,hIndex,url"
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                results = data.get("data", [])
                return results[0] if results else None

        except httpx.HTTPError as e:
            return None

    def get_paper_details(
        self,
        paper_id: str,
        fields: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific paper.

        Args:
            paper_id: Semantic Scholar paper ID
            fields: List of fields to include in response

        Returns:
            Paper details dict or None if not found
        """
        if fields is None:
            fields = [
                "paperId", "title", "abstract", "year", "citationCount",
                "venue", "authors", "externalIds", "url", "fieldsOfStudy",
                "influentialCitationCount", "references", "citations"
            ]

        url = f"{self.SEMANTIC_SCHOLAR_BASE_URL}/paper/{paper_id}"
        params = {"fields": ",".join(fields)}

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            return None


def search_publications(
    query: str,
    limit: int = 10,
    year: Optional[str] = None,
    use_local_db: bool = True
) -> List[Dict[str, Any]]:
    """
    Convenience function to search for publications.
    Searches local database first, then falls back to API.

    Args:
        query: Search query string
        limit: Maximum number of results
        year: Year filter (e.g., "2023" or "2020-2023")
        use_local_db: Whether to search local database first

    Returns:
        List of paper dictionaries
    """
    tool = PublicationSearchTool(use_local_db=use_local_db)
    return tool.search_papers(query, limit, year=year)


def search_author_publications(
    author_name: str,
    limit: int = 50,
    use_local_db: bool = True
) -> List[Dict[str, Any]]:
    """
    Search for publications by author name.
    Checks local database first, then falls back to Semantic Scholar API.

    Args:
        author_name: Name of the author
        limit: Maximum number of publications
        use_local_db: Whether to search local database first

    Returns:
        List of paper dictionaries
    """
    tool = PublicationSearchTool(use_local_db=use_local_db)

    # Try local database first
    if use_local_db:
        try:
            local_results = tool.get_professor_publications_local(
                professor_name=author_name,
                limit=limit
            )
            if local_results:
                return local_results
        except Exception:
            pass  # Fall through to API

    # Fall back to API
    author = tool.search_author(author_name)
    if not author:
        return []

    author_id = author.get("authorId")
    if not author_id:
        return []

    return tool.get_author_papers(author_id, limit, author_name=author_name)


def search_publications_by_professor(
    professor_name: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get publications for a specific professor from local database.

    Args:
        professor_name: Name of the professor
        limit: Maximum number of publications

    Returns:
        List of paper dictionaries
    """
    tool = PublicationSearchTool(use_local_db=True)
    return tool.get_professor_publications_local(professor_name, limit)