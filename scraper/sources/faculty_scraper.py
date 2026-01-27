from typing import Optional

import requests
from bs4 import BeautifulSoup

from scraper.sources.department_urls import DEPARTMENT_URLS


def extract_faculty_html(url):
    """Extracts faculty HTML from a single page."""
    try:
        response = requests.get(url)

        if response.status_code == 200:
            print(f"Request successful: {url}")
        else:
            print(f"Request failed: {url}")

        return response.text

    except requests.exceptions.RequestException as e:
        print("An error occurred: " + str(e))
        return ""


def extract_all_pages(base_url: str) -> list[str]:
    """Fetch all paginated pages from the directory."""
    pages = []
    page_num = 0

    while True:
        url = f"{base_url}?page={page_num}"
        html = extract_faculty_html(url)

        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")
        # Check if there are any faculty entries on this page
        if not soup.select("div.views-row"):
            break

        pages.append(html)
        page_num += 1

        # Safety limit to avoid infinite loops
        if page_num > 20:
            break

    print(f"Fetched {len(pages)} pages")
    return pages


def parse_all_faculty_pages(base_url: str) -> list[dict]:
    """Fetch and parse all pages of the faculty directory.

    Returns list of dicts with: name, department, email, website
    """
    all_faculty = []
    pages = extract_all_pages(base_url)
    site_base_url = extract_base_url(base_url)

    for html in pages:
        faculty_list = parse_faculty_directory(html, site_base_url)
        all_faculty.extend(faculty_list)

    print(f"Found {len(all_faculty)} faculty members total")

    # Fetch personal website from each profile page
    print("Fetching personal websites from profile pages...")
    for i, faculty in enumerate(all_faculty):
        if faculty["profile_url"]:
            profile_data = parse_profile_page(faculty["profile_url"])
            faculty["website"] = profile_data["website"]
        print(f"  [{i+1}/{len(all_faculty)}] {faculty['name']}: {faculty['website']}")

    return all_faculty


def extract_base_url(url: str) -> str:
    """Extract base URL (scheme + netloc) from a full URL."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def extract_email(row) -> Optional[str]:
    """Extract email from a faculty card, handling both link and text formats."""
    email_div = row.select_one("div.email")
    if not email_div:
        return None

    # Check for mailto link first
    email_link = email_div.select_one("a[href^='mailto:']")
    if email_link:
        return email_link["href"].replace("mailto:", "")

    # Otherwise parse text format like "name [at] cornell.edu"
    email_text = email_div.get_text(strip=True)
    email_text = email_text.replace(" [at] ", "@").replace("[at]", "@")
    email_text = email_text.replace(" [dot] ", ".").replace("[dot]", ".")
    return email_text if "@" in email_text else None


def extract_department(row) -> Optional[str]:
    """Extract department from a faculty card."""
    dept_div = row.select_one("div.department")
    if dept_div:
        return dept_div.get_text(strip=True)
    return None


def extract_department_from_url(url: str) -> Optional[str]:
    """Extract department name from profile URL."""
    if not url:
        return None

    if "duffield.cornell.edu" in url:
        return "Engineering (Duffield)"
    elif "cs.cornell.edu" in url:
        return "Computer Science"
    elif "engineering.cornell.edu" in url:
        return "Engineering"
    elif "ece.cornell.edu" in url:
        return "Electrical and Computer Engineering"
    elif "mae.cornell.edu" in url:
        return "Mechanical and Aerospace Engineering"

    return None


def parse_faculty_directory(html: str, base_url: str) -> list[dict]:
    """Parse faculty directory HTML and return list of faculty dicts."""
    soup = BeautifulSoup(html, "html.parser")
    faculty_list = []

    for row in soup.select("div.views-row"):
        name_div = row.select_one("div.name")
        if not name_div:
            continue

        name_link = name_div.select_one("a")
        name = name_link.get_text(strip=True) if name_link else name_div.get_text(strip=True)

        # Extract email and department from directory page
        email = extract_email(row)
        department = extract_department(row)

        # Find profile URL
        if name_link and name_link.get("href"):
            href = name_link["href"]
            # Handle both absolute and relative URLs
            if href.startswith("http"):
                profile_url = href
            else:
                profile_url = base_url + href
        else:
            profile_url = None

        # Use URL-based department if not found in HTML
        if not department:
            department = extract_department_from_url(profile_url)

        faculty_list.append({
            "name": name,
            "department": department,
            "email": email,
            "profile_url": profile_url,
            "website": None  # Will be filled in later
        })
        print(f"  {name}: {profile_url}")

    return faculty_list


def parse_profile_page(profile_url: str) -> dict:
    """Fetch and parse a faculty profile page for additional info."""
    result = {"website": None}

    if not profile_url:
        return result

    try:
        response = requests.get(profile_url, timeout=10)
        if response.status_code != 200:
            print(f"    Failed to fetch: {profile_url} (status {response.status_code})")
            return result

        soup = BeautifulSoup(response.text, "html.parser")

        # Format 1: Engineering profiles (li.person__contact-detail-item)
        for item in soup.select("li.person__contact-detail-item"):
            term = item.select_one("span.person__detail-term")
            if term and term.get_text(strip=True) in ("Website", "Research Website", "Personal Website", "Additional Links"):
                link = item.select_one("a[href]")
                if link:
                    result["website"] = link["href"]
                    break

        # Format 2: Bowers CIS profiles (div.right-rail-block with div.label)
        if not result["website"]:
            for block in soup.select("div.right-rail-block"):
                label = block.select_one("div.label")
                if label and label.get_text(strip=True) in ("Website", "Research Website", "Personal Website", "Additional Links"):
                    link = block.select_one("a[href]")
                    if link:
                        result["website"] = link["href"]
                        break

    except requests.exceptions.RequestException as e:
        print(f"    Error fetching {profile_url}: {e}")

    return result


if __name__ == "__main__":
    faculty = parse_all_faculty_pages(DEPARTMENT_URLS["computer_science"])
    print("\n=== Faculty Results ===")
    for f in faculty:
        print(f"Name: {f['name']}")
        print(f"  Department: {f['department']}")
        print(f"  Email: {f['email']}")
        print(f"  Website: {f['website']}")
        print()