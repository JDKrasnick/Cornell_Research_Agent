"""Generate embeddings from faculty research interests and store in ChromaDB.

This script:
1. Loads all faculty members with research interests from SQLite
2. Generates embeddings using sentence-transformers
3. Stores embeddings in ChromaDB for semantic search
"""

import logging
from pathlib import Path
from typing import List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from config.settings import settings
from scraper.sources.data import get_db_connection, get_all_faculty
from scraper.sources.data.publications_db import get_publications_for_professor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class FacultyEmbeddingBuilder:
    """Build and store faculty research interest embeddings."""

    def __init__(
        self,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        vector_store_path: Optional[Path] = None,
        collection_name: str = "faculty_research_interests",
        include_publications: bool = True,
        max_publications: int = 5
    ):
        """
        Initialize the embedding builder.

        Args:
            embedding_model_name: Name of the sentence-transformer model
            vector_store_path: Path to store ChromaDB data
            collection_name: Name of the ChromaDB collection
            include_publications: Whether to include publication content in embeddings
            max_publications: Maximum number of top publications to include (default: 5)
        """
        self.embedding_model_name = embedding_model_name
        self.vector_store_path = vector_store_path or settings.vector_store_path
        self.collection_name = collection_name
        self.include_publications = include_publications
        self.max_publications = max_publications

        logger.info(f"Initializing embedding model: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(embedding_model_name)

        logger.info(f"Initializing ChromaDB at: {self.vector_store_path}")
        self.vector_store_path.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.vector_store_path),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Faculty research interests embeddings"}
        )

    def clear_collection(self):
        """Clear all embeddings from the collection."""
        logger.info(f"Clearing collection: {self.collection_name}")
        try:
            self.chroma_client.delete_collection(name=self.collection_name)
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Faculty research interests embeddings"}
            )
            logger.info("Collection cleared successfully")
        except Exception as e:
            logger.warning(f"Error clearing collection: {e}")

    def build_embeddings(self, force_rebuild: bool = False):
        """
        Build embeddings for all faculty research interests.

        Args:
            force_rebuild: If True, clear existing embeddings before building
        """
        if force_rebuild:
            self.clear_collection()

        # Get all faculty from database
        logger.info("Loading faculty from database...")
        conn = get_db_connection()
        try:
            faculty_list = get_all_faculty(conn)
        finally:
            conn.close()

        # Filter faculty with research interests
        faculty_with_interests = [
            f for f in faculty_list
            if f.research_interests and f.research_interests.strip()
        ]

        if not faculty_with_interests:
            logger.warning("No faculty members with research interests found!")
            return

        logger.info(f"Found {len(faculty_with_interests)} faculty members with research interests")

        # Check existing embeddings
        existing_ids = set()
        try:
            existing_data = self.collection.get()
            if existing_data and existing_data['ids']:
                existing_ids = set(existing_data['ids'])
                logger.info(f"Found {len(existing_ids)} existing embeddings in collection")
        except Exception as e:
            logger.warning(f"Error checking existing embeddings: {e}")

        # Prepare data for embedding
        documents_to_embed = []
        metadatas = []
        ids = []

        logger.info(f"Building embeddings {'WITH' if self.include_publications else 'WITHOUT'} publication content...")

        for faculty in tqdm(faculty_with_interests, desc="Processing faculty"):
            faculty_id = f"faculty_{faculty.id}"

            # Skip if already embedded (unless force_rebuild)
            if not force_rebuild and faculty_id in existing_ids:
                continue

            # Start with name and research interests
            document_text = f"{faculty.name}: {faculty.research_interests}"

            # Add publication content if enabled
            if self.include_publications:
                try:
                    conn = get_db_connection()
                    publications = get_publications_for_professor(conn, faculty.name)
                    conn.close()

                    if publications:
                        # Sort by citation count and take top N
                        top_pubs = sorted(
                            publications,
                            key=lambda p: p.citation_count if p.citation_count else 0,
                            reverse=True
                        )[:self.max_publications]

                        # Add publication titles and abbreviated abstracts
                        pub_texts = []
                        for pub in top_pubs:
                            # Include title
                            pub_text = f"Paper: {pub.title}"

                            # Include first 300 chars of abstract if available
                            if pub.abstract:
                                abstract_preview = pub.abstract[:300]
                                if len(pub.abstract) > 300:
                                    abstract_preview += "..."
                                pub_text += f" - {abstract_preview}"

                            pub_texts.append(pub_text)

                        if pub_texts:
                            document_text += "\n\nKey Publications:\n" + "\n".join(pub_texts)

                except Exception as e:
                    logger.debug(f"Could not fetch publications for {faculty.name}: {e}")

            documents_to_embed.append(document_text)
            metadatas.append({
                "faculty_id": str(faculty.id),
                "name": faculty.name,
                "email": faculty.email or "",
                "department": faculty.department or "",
                "website_url": faculty.website_url or "",
                "profile_url": faculty.profile_url or "",
                "research_interests": faculty.research_interests
            })
            ids.append(faculty_id)

        if not documents_to_embed:
            logger.info("All faculty already embedded. Use force_rebuild=True to rebuild.")
            return

        logger.info(f"Generating embeddings for {len(documents_to_embed)} faculty members...")

        # Generate embeddings in batches
        batch_size = 32
        all_embeddings = []

        for i in tqdm(range(0, len(documents_to_embed), batch_size), desc="Generating embeddings"):
            batch = documents_to_embed[i:i + batch_size]
            batch_embeddings = self.embedding_model.encode(
                batch,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            all_embeddings.extend(batch_embeddings.tolist())

        # Store in ChromaDB
        logger.info("Storing embeddings in ChromaDB...")
        self.collection.add(
            embeddings=all_embeddings,
            documents=documents_to_embed,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(f"Successfully stored {len(documents_to_embed)} embeddings!")

    def get_collection_stats(self):
        """Get statistics about the collection."""
        count = self.collection.count()
        logger.info(f"Collection '{self.collection_name}' contains {count} embeddings")
        return count

    def search_similar_faculty(
        self,
        query: str,
        n_results: int = 5
    ) -> List[dict]:
        """
        Search for faculty with similar research interests.

        Args:
            query: Search query (student research interests)
            n_results: Number of results to return

        Returns:
            List of matching faculty with metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            query,
            convert_to_numpy=True
        ).tolist()

        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["metadatas", "documents", "distances"]
        )

        # Format results
        matches = []
        if results and results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                matches.append({
                    'id': results['ids'][0][i],
                    'name': results['metadatas'][0][i]['name'],
                    'research_interests': results['metadatas'][0][i]['research_interests'],
                    'email': results['metadatas'][0][i].get('email'),
                    'website_url': results['metadatas'][0][i].get('website_url'),
                    'department': results['metadatas'][0][i].get('department'),
                    'distance': results['distances'][0][i],
                    'document': results['documents'][0][i]
                })

        return matches


def main():
    """Main function to build embeddings."""
    import argparse

    parser = argparse.ArgumentParser(description="Build faculty research interest embeddings")
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Force rebuild all embeddings (clears existing ones)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="all-MiniLM-L6-v2",
        help="Sentence transformer model name (default: all-MiniLM-L6-v2)"
    )
    parser.add_argument(
        "--test-query",
        type=str,
        help="Test the embeddings with a sample query"
    )
    parser.add_argument(
        "--no-publications",
        action="store_true",
        help="Exclude publication content from embeddings (faster but less accurate)"
    )
    parser.add_argument(
        "--max-publications",
        type=int,
        default=5,
        help="Maximum number of top publications to include per faculty (default: 5)"
    )

    args = parser.parse_args()

    # Initialize builder
    builder = FacultyEmbeddingBuilder(
        embedding_model_name=args.model,
        include_publications=not args.no_publications,
        max_publications=args.max_publications
    )

    # Build embeddings
    logger.info("="*60)
    logger.info("Building Faculty Research Interest Embeddings")
    logger.info("="*60)

    builder.build_embeddings(force_rebuild=args.force_rebuild)

    # Show stats
    logger.info("\n" + "="*60)
    logger.info("Collection Statistics")
    logger.info("="*60)
    builder.get_collection_stats()

    # Test search if query provided
    if args.test_query:
        logger.info("\n" + "="*60)
        logger.info(f"Test Search: '{args.test_query}'")
        logger.info("="*60)

        results = builder.search_similar_faculty(args.test_query, n_results=5)

        for i, result in enumerate(results, 1):
            logger.info(f"\n{i}. {result['name']}")
            logger.info(f"   Research: {result['research_interests']}")
            logger.info(f"   Department: {result.get('department', 'N/A')}")
            logger.info(f"   Similarity: {1 - result['distance']:.3f}")


if __name__ == "__main__":
    main()