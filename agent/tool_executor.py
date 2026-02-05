import json

from tools.search_faculty import search_faculty
from tools.get_faculty_details import get_faculty_details
from tools.fetch_webpage import fetch_webpage
from tools.search_publications import search_author_publications
from tools.draft_email import draft_research_inquiry_email


def execute_search_faculty(query: str, department: str = None, top_k: int = 5) -> list:
    """Wrapper for search_faculty that maps top_k to n_results."""
    return search_faculty(query=query, n_results=top_k, min_similarity=0.0)


def execute_search_publications(faculty_name: str, limit: int = 5) -> list:
    """Wrapper for search_publications that uses author name."""
    return search_author_publications(author_name=faculty_name, limit=limit)


def execute_get_faculty_details(faculty_id: str) -> dict:
    """Wrapper for get_faculty_details that handles string IDs."""
    try:
        return get_faculty_details(faculty_id=int(faculty_id))
    except ValueError:
        # If faculty_id is not a valid integer, try it as a name
        return get_faculty_details(faculty_name=faculty_id)


def execute_draft_email(faculty_id: str, student_background: str, student_interests: str) -> dict:
    """Wrapper for draft_email that fetches faculty details first."""
    # Get faculty details
    faculty_details = execute_get_faculty_details(faculty_id)

    if not faculty_details:
        return {"success": False, "error": f"Faculty member with ID {faculty_id} not found"}

    # Extract student name from background if possible, otherwise use placeholder
    student_name = "Student"  # You might want to extract this from the input

    # Draft the email
    return draft_research_inquiry_email(
        faculty_name=faculty_details['name'],
        faculty_research_interests=faculty_details['research_interests'],
        student_name=student_name,
        student_background=student_background,
        student_interests=student_interests
    )


TOOL_FUNCTIONS = {
    "search_faculty": execute_search_faculty,
    "get_faculty_details": execute_get_faculty_details,
    "fetch_webpage": fetch_webpage,
    "search_publications": execute_search_publications,
    "draft_email": execute_draft_email,
}


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return the result as a string."""
    if tool_name not in TOOL_FUNCTIONS:
        return f"Error: Unknown tool '{tool_name}'"

    try:
        result = TOOL_FUNCTIONS[tool_name](**tool_input)
        # Convert result to string if needed
        if isinstance(result, dict) or isinstance(result, list):
            return json.dumps(result, indent=2)
        return str(result)
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"