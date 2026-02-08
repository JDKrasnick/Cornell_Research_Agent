"""Output formatting and display modules for CLI."""

from .tool_display import ToolDisplayManager
from .formatters import (
    format_faculty_table,
    format_faculty_details,
    format_publications_table,
    format_email_draft
)

__all__ = [
    'ToolDisplayManager',
    'format_faculty_table',
    'format_faculty_details',
    'format_publications_table',
    'format_email_draft',
]
