"""
LLM-based extraction of research information from faculty lab pages.

This module provides tools to scrape and extract structured research
information from faculty personal websites, lab pages, and academic
homepages using OpenAI GPT-4o for content analysis.
"""

import json
import logging
import time
from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from pydantic import BaseModel, Field

from config.settings import settings

logger = logging.getLogger(__name__)


class LabPageExtractionResult(BaseModel):
    """Structured extraction result from a faculty lab/personal page."""

    research_summary: Optional[str] = Field(
        None, description="1-3 paragraph summary of research focus and interests"
    )
    research_areas: List[str] = Field(
        default_factory=list, description="List of research keywords/topics/areas"
    )
    lab_url: Optional[str] = Field(
        None, description="URL to the faculty's research lab website"
    )
    publications_url: Optional[str] = Field(
        None, description="URL to publications/papers page"
    )
    personal_site_url: Optional[str] = Field(
        None, description="URL to separate personal/academic homepage"
    )
    source_url: str = Field(..., description="The URL that was scraped")
    extraction_successful: bool = Field(
        True, description="Whether extraction completed without errors"
    )
    error_message: Optional[str] = Field(
        None, description="Error description if extraction failed"
    )



EXTRACTION_SYSTEM_PROMPT = """You are an expert at extracting structured research information from academic faculty web pages.

Your task is to analyze HTML content from a faculty member's website and extract specific information about their research.

IMPORTANT GUIDELINES:
1. Extract information ONLY if it is clearly present in the content
2. For research_summary: Look for "About", "Research", "Bio" sections. Combine relevant paragraphs into a coherent 1-3 paragraph summary
3. For research_areas: Extract keywords, tags, or listed research topics. These might appear as bullet points, tags, or in prose
4. For lab_url: Look for links containing "lab", "group", "research group", or the PI's lab name
5. For publications_url: Look for links to "publications", "papers", "research", "Google Scholar", "DBLP"
6. For personal_site_url: Look for links to external personal homepages (different domain than current page)

RULES:
- Return ONLY valid JSON matching the specified schema
- Use null for fields where information is not found
- URLs must be absolute (start with http:// or https://) or relative paths
- Do NOT hallucinate or invent information not present in the HTML"""


EXTRACTION_USER_PROMPT = """Analyze this faculty web page and extract research information.

Source URL: {source_url}

Page Content:
```
{html_content}
```

Extract and return a JSON object with these fields:
- research_summary: string or null (1-3 paragraph research description)
- research_areas: array of strings (research keywords/topics, empty array if none found)
- lab_url: string or null (link to research lab)
- publications_url: string or null (link to publications page)
- personal_site_url: string or null (link to separate personal website)

Return ONLY valid JSON, no additional text."""



class HTMLFetcher:
    """Handles HTML fetching with retry logic and content cleaning."""

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (compatible; Cornell Research Bot/1.0)",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

    def fetch(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """
        Fetch HTML content from URL.

        Returns:
            Tuple of (html_content, error_message)
            If successful: (html, None)
            If failed: (None, error_description)
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text, None

            except requests.exceptions.Timeout:
                last_error = f"Timeout after {self.timeout}s"
            except requests.exceptions.HTTPError as e:
                last_error = f"HTTP {e.response.status_code}"
                if e.response.status_code in (404, 403, 410):
                    break  # Don't retry for permanent errors
            except requests.exceptions.RequestException as e:
                last_error = str(e)

            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (attempt + 1))

        return None, last_error

    def clean_html_for_llm(self, html: str, max_chars: int = 50000) -> str:
        """
        Clean and truncate HTML for LLM processing.

        Removes scripts, styles, and irrelevant elements while
        preserving text content and important links.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove non-content elements
        for element in soup(
            ["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe"]
        ):
            element.decompose()

        # Get text with links preserved
        text_parts = []
        for element in soup.find_all(
            ["p", "h1", "h2", "h3", "h4", "li", "a", "div", "span"]
        ):
            if element.name == "a" and element.get("href"):
                text = element.get_text(strip=True)
                href = element["href"]
                if text and len(text) > 2:
                    text_parts.append(f"[{text}]({href})")
            else:
                text = element.get_text(strip=True)
                if text and len(text) > 10:
                    text_parts.append(text)

        cleaned = "\n".join(text_parts)

        # Truncate if needed
        if len(cleaned) > max_chars:
            cleaned = cleaned[:max_chars] + "\n[CONTENT TRUNCATED]"

        return cleaned


# ========================
class OpenAIExtractor:
    """OpenAI GPT client for structured extraction."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.llm_model
        self.client = OpenAI(api_key=self.api_key)

    def extract_structured(
        self, system_prompt: str, user_prompt: str
    ) -> dict:
        """Extract structured data using the LLM."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=2000,
        )

        content = response.choices[0].message.content
        return json.loads(content)


class LabPageExtractor:
    """
    Extracts research information from faculty lab/personal pages
    using LLM-based content analysis.
    """

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.fetcher = HTMLFetcher(timeout=timeout, max_retries=max_retries)
        self.extractor = OpenAIExtractor(api_key=api_key, model=model)

    def _resolve_urls(self, data: dict, base_url: str) -> dict:
        """Convert relative URLs to absolute URLs."""
        url_fields = ["lab_url", "publications_url", "personal_site_url"]

        for field in url_fields:
            url = data.get(field)
            if url and not url.startswith(("http://", "https://")):
                data[field] = urljoin(base_url, url)

        return data

    def extract(self, url: str) -> LabPageExtractionResult:
        """
        Extract research information from a faculty page URL.

        Args:
            url: The faculty page URL to scrape

        Returns:
            LabPageExtractionResult with extracted data or error info
        """
        # Step 1: Fetch HTML
        html, fetch_error = self.fetcher.fetch(url)

        if fetch_error:
            return LabPageExtractionResult(
                source_url=url,
                extraction_successful=False,
                error_message=f"Failed to fetch page: {fetch_error}",
            )

        # Step 2: Clean HTML for LLM
        cleaned_html = self.fetcher.clean_html_for_llm(html)

        if not cleaned_html.strip():
            return LabPageExtractionResult(
                source_url=url,
                extraction_successful=True,
                error_message="Page content was empty after cleaning",
            )

        # Step 3: Call LLM for extraction
        try:
            user_prompt = EXTRACTION_USER_PROMPT.format(
                source_url=url, html_content=cleaned_html
            )

            extracted_data = self.extractor.extract_structured(
                system_prompt=EXTRACTION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )

            # Resolve relative URLs
            extracted_data = self._resolve_urls(extracted_data, url)

            return LabPageExtractionResult(
                research_summary=extracted_data.get("research_summary"),
                research_areas=extracted_data.get("research_areas", []),
                lab_url=extracted_data.get("lab_url"),
                publications_url=extracted_data.get("publications_url"),
                personal_site_url=extracted_data.get("personal_site_url"),
                source_url=url,
                extraction_successful=True,
            )

        except json.JSONDecodeError as e:
            return LabPageExtractionResult(
                source_url=url,
                extraction_successful=False,
                error_message=f"Failed to parse LLM response as JSON: {e}",
            )
        except Exception as e:
            return LabPageExtractionResult(
                source_url=url,
                extraction_successful=False,
                error_message=f"LLM extraction failed: {type(e).__name__}: {e}",
            )

    def extract_batch(
        self,
        urls: List[str],
        delay_between_requests: float = 0.5,
    ) -> List[LabPageExtractionResult]:
        """
        Extract from multiple URLs with rate limiting.

        Args:
            urls: List of URLs to process
            delay_between_requests: Seconds to wait between requests

        Returns:
            List of extraction results in same order as input URLs
        """
        results = []

        for i, url in enumerate(urls):
            logger.info(f"Processing [{i + 1}/{len(urls)}]: {url}")

            result = self.extract(url)
            results.append(result)

            # Rate limiting (skip on last item)
            if i < len(urls) - 1:
                time.sleep(delay_between_requests)

        return results



def extract_lab_page(url: str) -> LabPageExtractionResult:
    """
    Extract research information from a single faculty page URL.

    Uses default configuration from settings.

    Args:
        url: The faculty page URL to scrape

    Returns:
        LabPageExtractionResult with extracted data
    """
    extractor = LabPageExtractor()
    return extractor.extract(url)


def extract_lab_pages_batch(
    urls: List[str], delay: float = 0.5
) -> List[LabPageExtractionResult]:
    """
    Extract from multiple URLs with rate limiting.

    Args:
        urls: List of URLs to process
        delay: Seconds to wait between requests (default 0.5)

    Returns:
        List of extraction results in same order as input URLs
    """
    extractor = LabPageExtractor()
    return extractor.extract_batch(urls, delay_between_requests=delay)



if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m scraper.sources.lab_pages <url>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"Extracting from: {url}")

    result = extract_lab_page(url)

    print(f"\n=== Extraction Result ===")
    print(f"Source: {result.source_url}")
    print(f"Success: {result.extraction_successful}")

    if result.research_summary:
        summary = result.research_summary
        if len(summary) > 500:
            summary = summary[:500] + "..."
        print(f"\nResearch Summary:\n{summary}")

    if result.research_areas:
        print(f"\nResearch Areas: {', '.join(result.research_areas)}")

    print(f"\nLab URL: {result.lab_url}")
    print(f"Publications URL: {result.publications_url}")
    print(f"Personal Site URL: {result.personal_site_url}")

    if result.error_message:
        print(f"\nError: {result.error_message}")