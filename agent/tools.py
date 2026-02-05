# agent/tools.py

TOOLS = [
    {
        "name": "search_faculty",
        "description": "Search for Cornell faculty members whose research matches the given query. Use this to find professors working in areas the student is interested in. Returns top matches ranked by relevance.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A description of research interests to search for (e.g., 'machine learning for drug discovery' or 'computer vision and robotics')"
                },
                "department": {
                    "type": "string",
                    "description": "Optional: limit search to a specific department (e.g., 'CS', 'ECE', 'INFO')"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results to return (default 5)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_faculty_details",
        "description": "Get detailed information about a specific faculty member, including their full research description, lab information, and recent publications.",
        "input_schema": {
            "type": "object",
            "properties": {
                "faculty_id": {
                    "type": "string",
                    "description": "The unique ID of the faculty member"
                }
            },
            "required": ["faculty_id"]
        }
    },
    {
        "name": "fetch_webpage",
        "description": "Fetch and read the contents of a webpage. Use this to get more information from lab websites, faculty pages, or other URLs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "search_publications",
        "description": "Search for recent publications by a faculty member. Returns titles, years, and abstracts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "faculty_name": {
                    "type": "string",
                    "description": "The name of the faculty member"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of publications to return (default 5)"
                }
            },
            "required": ["faculty_name"]
        }
    },
    {
        "name": "draft_email",
        "description": "Draft a personalized outreach email from a student to a faculty member. The email will reference the professor's research and the student's interests.",
        "input_schema": {
            "type": "object",
            "properties": {
                "faculty_id": {
                    "type": "string",
                    "description": "The faculty member to address the email to"
                },
                "student_background": {
                    "type": "string",
                    "description": "Brief description of the student's background, skills, and relevant coursework"
                },
                "student_interests": {
                    "type": "string",
                    "description": "What the student is interested in and why this professor's work appeals to them"
                }
            },
            "required": ["faculty_id", "student_background", "student_interests"]
        }
    }
]