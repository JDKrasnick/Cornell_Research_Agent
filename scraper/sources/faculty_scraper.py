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

    # First, fetch the base page
    html = extract_faculty_html(base_url)
    if not html:
        return pages
    pages.append(html)

    # Try pagination with ?page=N
    page_num = 1
    while page_num <= 20:
        url = f"{base_url}?page={page_num}"
        html = extract_faculty_html(url)

        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")
        # Check if page has any content (faculty rows or profile links)
        has_faculty_rows = soup.select("div.views-row")
        has_profile_links = soup.find_all("a", href=lambda h: h and "/people/" in h)

        if not has_faculty_rows and not has_profile_links:
            break

        pages.append(html)
        page_num += 1

    print(f"Fetched {len(pages)} pages")
    return pages


def parse_all_faculty_pages(base_url: str) -> list[dict]:
    """Fetch and parse all pages of the faculty directory.

    Returns list of dicts with: name, department, email, website, profile_url
    Uses a generic parser that extracts names and their linked profile URLs.
    """
    all_faculty = []
    pages = extract_all_pages(base_url)
    site_base_url = extract_base_url(base_url)

    for html in pages:
        faculty_list = parse_faculty_generic(html, site_base_url)
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


def is_likely_name(text: str) -> bool:
    """Check if text looks like a person's name."""
    if not text or len(text) < 3 or len(text) > 50:
        return False

    # Skip common non-name text
    skip_words = {"people", "faculty", "staff", "home", "about", "contact", "research",
                  "publications", "news", "events", "directory", "search", "menu",
                  "skip to", "main content", "navigation", "read more", "view profile"}
    if text.lower() in skip_words:
        return False

    # Names typically have at least 2 parts and contain mostly letters/spaces
    words = text.split()
    if len(words) < 2:
        return False

    # Check that most characters are letters or spaces
    alpha_count = sum(1 for c in text if c.isalpha() or c.isspace())
    if alpha_count / len(text) < 0.8:
        return False

    return True


def parse_faculty_generic(html: str, base_url: str) -> list[dict]:
    """Generic parser that extracts faculty names and their linked profile URLs.

    Works by finding all links where the text looks like a name and the href
    looks like a profile URL.
    """
    soup = BeautifulSoup(html, "html.parser")
    faculty_list = []
    seen_urls = set()

    # Strategy 1: Try CS-style parsing (div.views-row with div.name)
    for row in soup.select("div.views-row"):
        name_div = row.select_one("div.name")
        if not name_div:
            continue

        name_link = name_div.select_one("a")
        name = name_link.get_text(strip=True) if name_link else name_div.get_text(strip=True)

        if not name:
            continue

        email = extract_email(row)
        department = extract_department(row)

        profile_url = None
        if name_link and name_link.get("href"):
            href = name_link["href"]
            if href.startswith("http"):
                profile_url = href
            else:
                profile_url = base_url + href

        if profile_url and profile_url not in seen_urls:
            seen_urls.add(profile_url)
            if not department:
                department = extract_department_from_url(profile_url)

            faculty_list.append({
                "name": name,
                "department": department,
                "email": email,
                "profile_url": profile_url,
                "website": None
            })
            print(f"  {name}: {profile_url}")

    # Strategy 2: Find links that look like faculty profiles (e.g., /people/name/)
    for link in soup.find_all("a", href=True):
        href = link["href"]
        name = link.get_text(strip=True)

        # Skip if not a profile-like URL
        if "/people/" not in href:
            continue

        # Skip index pages
        parts = href.rstrip("/").split("/")
        if len(parts) < 2 or parts[-1] == "people":
            continue

        # Check if text looks like a name
        if not is_likely_name(name):
            continue

        # Build absolute URL
        if href.startswith("http"):
            profile_url = href
        else:
            profile_url = base_url + href

        # Skip duplicates
        if profile_url in seen_urls:
            continue
        seen_urls.add(profile_url)

        # Try to find email from nearby mailto link
        email = None
        parent = link.find_parent(["div", "article", "section", "li"])
        if parent:
            mailto = parent.find("a", href=lambda h: h and h.startswith("mailto:"))
            if mailto:
                email = mailto["href"].replace("mailto:", "")

        faculty_list.append({
            "name": name,
            "department": extract_department_from_url(profile_url),
            "email": email,
            "profile_url": profile_url,
            "website": None
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
    from scraper.sources.data import get_db_connection, init_faculty_table, store_faculty

    all_faculty = []
    seen_names = set()

    for dept_name, dept_url in DEPARTMENT_URLS.items():
        print(f"\n{'='*60}")
        print(f"Scraping {dept_name}...")
        print(f"{'='*60}")

        faculty = parse_all_faculty_pages(dept_url)

        for f in faculty:
            if f["name"] in seen_names:
                for existing in all_faculty:
                    if existing["name"] == f["name"]:
                        if not existing["website"] and f["website"]:
                            existing["website"] = f["website"]
                        if not existing["email"] and f["email"]:
                            existing["email"] = f["email"]
                        break
            else:
                seen_names.add(f["name"])
                all_faculty.append(f)

    # Store in database
    print(f"\n{'='*60}")
    print(f"Storing {len(all_faculty)} faculty members in database...")
    print(f"{'='*60}")

    conn = get_db_connection()
    try:
        init_faculty_table(conn)
        count = store_faculty(conn, all_faculty)
        print(f"Successfully stored {count} faculty members")
    finally:
        conn.close()

    print(f"\n{'='*60}")
    print(f"=== Faculty Results ({len(all_faculty)} total) ===")
    print(f"{'='*60}")
    for f in all_faculty:
        print(f"Name: {f['name']}")
        print(f"  Department: {f['department']}")
        print(f"  Email: {f['email']}")
        print(f"  Website: {f['website']}")
        print(f"  Profile: {f['profile_url']}")
        print()