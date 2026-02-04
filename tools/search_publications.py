"""Semantic Scholar / arXiv API wrapper."""

from typing import List, Dict, Any, Optional
import time

import httpx

from config.settings import settings


class PublicationSearchTool:
    """Tool for searching academic publications via Semantic Scholar API."""

    SEMANTIC_SCHOLAR_BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the publication search tool.

        Args:
            api_key: Semantic Scholar API key (optional but recommended)
        """
        self.api_key = api_key or settings.semantic_scholar_api_key
        self.headers = {}
        if self.api_key:
            self.headers["x-api-key"] = self.api_key

    def search_papers(
        self,
        query: str,
        limit: int = 10,
        fields: Optional[List[str]] = None,
        year: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for papers by keyword query.

        Args:
            query: Search query string
            limit: Maximum number of results (max 100)
            fields: List of fields to include in response
            year: Year filter (e.g., "2023" or "2020-2023")

        Returns:
            List of paper dictionaries
        """
        if fields is None:
            fields = [
                "paperId", "title", "abstract", "year", "citationCount",
                "venue", "authors", "externalIds", "url"
            ]

        url = f"{self.SEMANTIC_SCHOLAR_BASE_URL}/paper/search"
        params = {
            "query": query,
            "limit": min(limit, 100),
            "fields": ",".join(fields)
        }

        if year:
            params["year"] = year

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                return data.get("data", [])

        except httpx.HTTPError as e:
            return []

    def get_author_papers(
        self,
        author_id: str,
        limit: int = 50,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get papers by a specific author.

        Args:
            author_id: Semantic Scholar author ID
            limit: Maximum number of papers to return
            fields: List of fields to include in response

        Returns:
            List of paper dictionaries
        """
        if fields is None:
            fields = [
                "paperId", "title", "abstract", "year", "citationCount",
                "venue", "externalIds", "url"
            ]

        url = f"{self.SEMANTIC_SCHOLAR_BASE_URL}/author/{author_id}/papers"
        params = {
            "limit": min(limit, 1000),
            "fields": ",".join(fields)
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                return data.get("data", [])

        except httpx.HTTPError as e:
            return []

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
    year: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to search for publications.

    Args:
        query: Search query string
        limit: Maximum number of results
        year: Year filter (e.g., "2023" or "2020-2023")

    Returns:
        List of paper dictionaries
    """
    tool = PublicationSearchTool()
    return tool.search_papers(query, limit, year=year)


def search_author_publications(author_name: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Search for publications by author name.

    Args:
        author_name: Name of the author
        limit: Maximum number of publications

    Returns:
        List of paper dictionaries
    """
    tool = PublicationSearchTool()

    # First, find the author
    author = tool.search_author(author_name)
    if not author:
        return []

    # Then get their papers
    author_id = author.get("authorId")
    if not author_id:
        return []

    return tool.get_author_papers(author_id, limit)