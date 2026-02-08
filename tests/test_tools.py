"""Simple test script to verify tool implementations."""

from tools import (
    search_faculty,
    get_faculty_details,
    search_publications,
    search_publications_by_professor,
    fetch_webpage,
    draft_research_inquiry_email
)


def test_search_faculty():
    """Test faculty search tool."""
    print("\n" + "="*60)
    print("Testing Faculty Search Tool")
    print("="*60)

    try:
        results = search_faculty(
            query="machine learning and computer vision",
            n_results=3
        )
        print(f"✓ Found {len(results)} faculty members")
        for i, faculty in enumerate(results[:2], 1):
            print(f"\n{i}. {faculty['name']}")
            print(f"   Research: {faculty['research_interests'][:100]}...")
            print(f"   Similarity: {faculty['similarity_score']:.3f}")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_get_faculty_details():
    """Test faculty details retrieval."""
    print("\n" + "="*60)
    print("Testing Faculty Details Tool")
    print("="*60)

    try:
        # Test with a known faculty name
        details = get_faculty_details(
            faculty_name="Abe Davis",
            include_publications=True,
            max_publications=3
        )

        if details:
            print(f"✓ Retrieved details for {details['name']}")
            print(f"   Email: {details.get('email', 'N/A')}")
            print(f"   Department: {details.get('department', 'N/A')}")
            print(f"   Publications: {details.get('total_publications', 0)}")
        else:
            print("✗ Faculty not found")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_search_publications():
    """Test publication search tool."""
    print("\n" + "="*60)
    print("Testing Publication Search Tool (Local DB + API)")
    print("="*60)

    try:
        # Test local database search
        papers = search_publications(
            query="machine learning",
            limit=5,
            use_local_db=True
        )
        print(f"✓ Found {len(papers)} papers (local DB + API)")
        for i, paper in enumerate(papers[:3], 1):
            source = paper.get('source', 'unknown')
            print(f"\n{i}. {paper.get('title', 'N/A')}")
            print(f"   Year: {paper.get('year', 'N/A')}")
            print(f"   Citations: {paper.get('citationCount', 0)}")
            print(f"   Source: {source}")
            if source == 'local_db':
                print(f"   Professor: {paper.get('professor_name', 'N/A')}")

        # Test professor-specific search
        print("\n" + "-"*60)
        print("Testing Professor Publications (Local DB only)")
        professor_pubs = search_publications_by_professor("Abe Davis", limit=3)
        print(f"✓ Found {len(professor_pubs)} publications for Abe Davis")
        for i, paper in enumerate(professor_pubs[:2], 1):
            print(f"\n{i}. {paper.get('title', 'N/A')[:60]}...")
            print(f"   Year: {paper.get('year', 'N/A')}")
            print(f"   Citations: {paper.get('citationCount', 0)}")

    except Exception as e:
        print(f"✗ Error: {e}")


def test_fetch_webpage():
    """Test webpage fetcher tool."""
    print("\n" + "="*60)
    print("Testing Webpage Fetcher Tool")
    print("="*60)

    try:
        result = fetch_webpage(
            url="https://www.cs.cornell.edu/",
            extract_text=True,
            max_text_length=200
        )

        if result['success']:
            print(f"✓ Successfully fetched webpage")
            print(f"   Title: {result.get('title', 'N/A')}")
            print(f"   Text preview: {result.get('text', '')[:100]}...")
        else:
            print(f"✗ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_draft_email():
    """Test email drafting tool."""
    print("\n" + "="*60)
    print("Testing Email Draft Tool")
    print("="*60)

    try:
        email = draft_research_inquiry_email(
            faculty_name="Dr. Smith",
            faculty_research_interests="machine learning, computer vision",
            student_name="Alice Johnson",
            student_background="CS senior interested in AI research",
            student_interests="computer vision and deep learning"
        )

        if email['success']:
            print("✓ Successfully generated email draft")
            print(f"   Subject: {email.get('subject', 'N/A')}")
            print(f"   Body length: {len(email.get('body', ''))} characters")
        else:
            print(f"✗ Failed: {email.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    print("\nTesting Cornell Research Agent Tools")
    print("="*60)

    # Run tests
    test_search_faculty()
    test_get_faculty_details()
    test_search_publications()
    test_fetch_webpage()
    test_draft_email()

    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)
