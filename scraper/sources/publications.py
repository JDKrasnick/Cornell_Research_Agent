import requests
from typing import List
from lab_pages import LabPageExtractionResult  # Assuming this is your imported Pydantic model

SEMANTIC_SCHOLAR_SEARCH_API = "https://api.semanticscholar.org/graph/v1/author/search"
SEMANTIC_SCHOLAR_AUTHOR_PAPERS_API = "https://api.semanticscholar.org/graph/v1/author/{author_id}/papers"


def populate_labpage_from_semantic_scholar(
    professor_name: str,
    partial_result: LabPageExtractionResult,
    top_n_papers: int = 5
) -> LabPageExtractionResult:
    """
    Populate attributes in LabPageExtractionResult using Semantic Scholar API.
    """
    try:

        search_resp = requests.get(
            SEMANTIC_SCHOLAR_SEARCH_API,
            params={"query": professor_name, "fields": "name,url,fieldsOfStudy,authorId"}
        )
        search_resp.raise_for_status()
        search_data = search_resp.json()

        if not search_data.get("data"):
            partial_result.extraction_successful = False
            partial_result.error_message = "Author not found on Semantic Scholar."
            return partial_result

        author = search_data["data"][0]
        author_id = author["authorId"]

        # Fill research areas and publications URL
        partial_result.research_areas = author.get("fieldsOfStudy", [])
        partial_result.publications_url = author.get("url")
        partial_result.source_url = author.get("url")
        partial_result.lab_url = None
        partial_result.personal_site_url = None


        papers_resp = requests.get(
            SEMANTIC_SCHOLAR_AUTHOR_PAPERS_API.format(author_id=author_id),
            params={"fields": "title,abstract,citationCount", "limit": 20}
        )
        papers_resp.raise_for_status()
        papers = papers_resp.json().get("data", [])

        if papers:

            top_papers = sorted(
                papers, key=lambda x: x.get("citationCount", 0), reverse=True
            )[:top_n_papers]


            abstracts = [p.get("abstract", "") for p in top_papers if p.get("abstract")]
            if abstracts:
                combined_text = " ".join(abstracts)
                partial_result.research_summary = ". ".join(combined_text.split(".")[:2]) + "."
            else:
                partial_result.research_summary = None
        else:
            partial_result.research_summary = None

        partial_result.extraction_successful = True

    except Exception as e:
        partial_result.extraction_successful = False
        partial_result.error_message = str(e)

    return partial_result
