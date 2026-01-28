"""
Scrape faculty names from Cornell website and fetch their top publications.

This script:
1. Scrapes faculty names from Cornell department pages
2. For each faculty member, fetches their top 10 most cited publications from Semantic Scholar
3. Stores all publications in the SQLite database
"""

import sys
import time
from pathlib import Path

#
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scraper.sources.faculty_scraper import parse_all_faculty_pages
from scraper.sources.department_urls import DEPARTMENT_URLS
from scraper.sources.publications import scrape_and_store_publications


def fetch_with_retry(name: str, max_retries: int = 3, initial_backoff: float = 60.0):
    """
    Fetch publications with retry and exponential backoff for rate limits.

    Args:
        name: Professor name to search
        max_retries: Maximum number of retries on rate limit
        initial_backoff: Initial wait time in seconds when rate limited

    Returns:
        Tuple of (count, error)
    """
    backoff = initial_backoff

    for attempt in range(max_retries + 1):
        count, error = scrape_and_store_publications(name, top_n=10)

        if error and "rate limit" in error.lower():
            if attempt < max_retries:
                print(f"Rate limited, waiting {backoff:.0f}s...", end=" ", flush=True)
                time.sleep(backoff)
                backoff *= 2  # Exponential backoff
                print("Retrying...", end=" ", flush=True)
                continue

        return count, error

    return 0, "Max retries exceeded due to rate limiting"


def scrape_department_publications(department_key: str, delay_between_requests: float = 3.0):
    """
    Scrape all faculty from a department and fetch their publications.

    Args:
        department_key: Key from DEPARTMENT_URLS dict
        delay_between_requests: Seconds to wait between Semantic Scholar API calls
    """
    if department_key not in DEPARTMENT_URLS:
        print(f"Error: Unknown department '{department_key}'")
        print(f"Available departments: {list(DEPARTMENT_URLS.keys())}")
        return

    url = DEPARTMENT_URLS[department_key]
    print(f"\n{'='*60}")
    print(f"Scraping faculty from: {department_key}")
    print(f"URL: {url}")
    print(f"{'='*60}\n")

    # Step 1: Get faculty list
    faculty_list = parse_all_faculty_pages(url)

    if not faculty_list:
        print("No faculty found. Exiting.")
        return

    print(f"\n{'='*60}")
    print(f"Found {len(faculty_list)} faculty members")
    print(f"Fetching publications for each (delay: {delay_between_requests}s)...")
    print(f"{'='*60}\n")

    # Step 2: Fetch publications for each faculty member
    success_count = 0
    error_count = 0

    for i, faculty in enumerate(faculty_list, 1):
        name = faculty["name"]
        print(f"[{i}/{len(faculty_list)}] {name}...", end=" ", flush=True)

        count, error = fetch_with_retry(name)

        if error:
            print(f"ERROR: {error}")
            error_count += 1
        elif count == 0:
            print("No publications found")
        else:
            print(f"Stored {count} publications")
            success_count += 1

        # Rate limiting between requests
        if i < len(faculty_list):
            time.sleep(delay_between_requests)

    print(f"\n{'='*60}")
    print(f"Completed!")
    print(f"  Successful: {success_count}/{len(faculty_list)}")
    print(f"  Errors: {error_count}/{len(faculty_list)}")
    print(f"{'='*60}")


def scrape_all_departments(delay_between_requests: float = 3.0):
    """Scrape publications for all configured departments."""
    for department_key in DEPARTMENT_URLS:
        scrape_department_publications(department_key, delay_between_requests)
        print("\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Scrape Cornell faculty and their publications"
    )
    parser.add_argument(
        "department",
        nargs="?",
        default=None,
        help=f"Department to scrape. Options: {list(DEPARTMENT_URLS.keys())}. "
             f"If not specified, scrapes all departments."
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Delay between API requests in seconds (default: 3.0)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available departments and exit"
    )

    args = parser.parse_args()

    if args.list:
        print("Available departments:")
        for key, url in DEPARTMENT_URLS.items():
            print(f"  {key}: {url}")
        sys.exit(0)

    if args.department:
        scrape_department_publications(args.department, args.delay)
    else:
        print("Scraping all departments...")
        scrape_all_departments(args.delay)