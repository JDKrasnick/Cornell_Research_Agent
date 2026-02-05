"""Agent tools for search and retrieval."""

from .search_faculty import search_faculty, FacultySearchTool
from .get_faculty_details import get_faculty_details
from .search_publications import (
    search_publications,
    search_author_publications,
    search_publications_by_professor,
    PublicationSearchTool
)
from .fetch_webpage import fetch_webpage, extract_contact_info, WebPageFetcherTool
from .draft_email import draft_research_inquiry_email, EmailDraftTool

__all__ = [
    # Faculty search
    'search_faculty',
    'FacultySearchTool',
    'get_faculty_details',

    # Publications
    'search_publications',
    'search_author_publications',
    'search_publications_by_professor',
    'PublicationSearchTool',

    # Web scraping
    'fetch_webpage',
    'extract_contact_info',
    'WebPageFetcherTool',

    # Email drafting
    'draft_research_inquiry_email',
    'EmailDraftTool',
]