"""Generic URL fetcher + parser."""

from typing import Optional, Dict, Any
import re

import httpx
from bs4 import BeautifulSoup


class WebPageFetcherTool:
    """Tool for fetching and parsing web pages."""

    def __init__(self, timeout: float = 30.0):
        """
        Initialize the webpage fetcher tool.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    def fetch(
        self,
        url: str,
        extract_text: bool = True,
        extract_links: bool = False,
        max_text_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch and parse a webpage.

        Args:
            url: URL to fetch
            extract_text: Whether to extract and clean text content
            extract_links: Whether to extract links from the page
            max_text_length: Maximum length of text to return (None for unlimited)

        Returns:
            Dictionary with page content and metadata
        """
        result = {
            'url': url,
            'success': False,
            'error': None,
            'title': None,
            'text': None,
            'html': None,
            'links': None
        }

        try:
            # Fetch the page
            with httpx.Client(
                timeout=self.timeout,
                follow_redirects=True,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; ResearchBot/1.0)'}
            ) as client:
                response = client.get(url)
                response.raise_for_status()

                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract title
                title_tag = soup.find('title')
                result['title'] = title_tag.get_text(strip=True) if title_tag else None

                # Extract text content
                if extract_text:
                    # Remove script and style elements
                    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                        element.decompose()

                    # Get text
                    text = soup.get_text(separator=' ', strip=True)

                    # Clean up whitespace
                    text = re.sub(r'\s+', ' ', text)

                    # Truncate if needed
                    if max_text_length and len(text) > max_text_length:
                        text = text[:max_text_length] + '...'

                    result['text'] = text

                # Extract links
                if extract_links:
                    links = []
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        link_text = link.get_text(strip=True)

                        # Convert relative URLs to absolute
                        if href.startswith('/'):
                            from urllib.parse import urljoin
                            href = urljoin(url, href)

                        links.append({
                            'url': href,
                            'text': link_text
                        })

                    result['links'] = links

                # Store raw HTML if needed (for debugging)
                # result['html'] = response.text

                result['success'] = True

        except httpx.HTTPError as e:
            result['error'] = f"HTTP error: {str(e)}"
        except Exception as e:
            result['error'] = f"Error: {str(e)}"

        return result

    def extract_contact_info(self, url: str) -> Dict[str, Any]:
        """
        Extract contact information from a webpage.

        Args:
            url: URL to fetch

        Returns:
            Dictionary with extracted email addresses and other contact info
        """
        result = self.fetch(url, extract_text=True)

        if not result['success']:
            return result

        text = result.get('text', '')
        html = result.get('html', '')

        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = list(set(re.findall(email_pattern, text)))

        # Extract phone numbers (simple pattern)
        phone_pattern = r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'
        phones = list(set([
            '-'.join(match) for match in re.findall(phone_pattern, text)
        ]))

        result['emails'] = emails
        result['phones'] = phones

        return result


def fetch_webpage(
    url: str,
    extract_text: bool = True,
    extract_links: bool = False,
    max_text_length: Optional[int] = 10000
) -> Dict[str, Any]:
    """
    Convenience function to fetch and parse a webpage.

    Args:
        url: URL to fetch
        extract_text: Whether to extract and clean text content
        extract_links: Whether to extract links from the page
        max_text_length: Maximum length of text to return

    Returns:
        Dictionary with page content and metadata
    """
    tool = WebPageFetcherTool()
    return tool.fetch(url, extract_text, extract_links, max_text_length)


def extract_contact_info(url: str) -> Dict[str, Any]:
    """
    Extract contact information from a webpage.

    Args:
        url: URL to fetch

    Returns:
        Dictionary with extracted contact information
    """
    tool = WebPageFetcherTool()
    return tool.extract_contact_info(url)