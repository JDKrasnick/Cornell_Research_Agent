"""Data models for scraped research information."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Publication:
    """Represents a single academic publication."""

    paper_id: str
    title: str
    abstract: Optional[str]
    citation_count: int
    year: Optional[int]
    venue: Optional[str]
    url: Optional[str]
    professor_name: str
    author_id: str
    fetched_at: datetime