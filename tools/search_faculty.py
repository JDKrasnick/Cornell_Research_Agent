"""Vector search over faculty profiles."""

from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from config.settings import settings


class FacultySearchTool:
    """Tool for semantic search over faculty research interests."""

    def __init__(
        self,
        embedding_model_name: str = "all-MiniLM-L6-v2",
        vector_store_path: Optional[Path] = None,
        collection_name: str = "faculty_research_interests"
    ):
        """
        Initialize the faculty search tool.

        Args:
            embedding_model_name: Name of the sentence-transformer model
            vector_store_path: Path to ChromaDB data
            collection_name: Name of the ChromaDB collection
        """
        self.embedding_model_name = embedding_model_name
        self.vector_store_path = vector_store_path or settings.vector_store_path
        self.collection_name = collection_name

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model_name)

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.vector_store_path),
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )

        # Get collection
        try:
            self.collection = self.chroma_client.get_collection(name=collection_name)
        except Exception:
            raise ValueError(
                f"Collection '{collection_name}' not found. "
                "Run 'python scripts/build_embeddings.py' first."
            )

    def search(
        self,
        query: str,
        n_results: int = 5,
        min_similarity: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for faculty members with research interests matching the query.

        Args:
            query: Search query describing research interests
            n_results: Maximum number of results to return
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of faculty matches with metadata and similarity scores
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
                # Convert distance to similarity (1 - normalized distance)
                distance = results['distances'][0][i]
                similarity = 1 - distance

                # Filter by minimum similarity
                if similarity < min_similarity:
                    continue

                metadata = results['metadatas'][0][i]
                matches.append({
                    'faculty_id': metadata.get('faculty_id'),
                    'name': metadata.get('name'),
                    'email': metadata.get('email'),
                    'department': metadata.get('department'),
                    'website_url': metadata.get('website_url'),
                    'profile_url': metadata.get('profile_url'),
                    'research_interests': metadata.get('research_interests'),
                    'similarity_score': round(similarity, 4),
                    'matched_text': results['documents'][0][i]
                })

        return matches


def search_faculty(
    query: str,
    n_results: int = 5,
    min_similarity: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Convenience function to search for faculty.

    Args:
        query: Search query describing research interests
        n_results: Maximum number of results to return
        min_similarity: Minimum similarity threshold (0-1)

    Returns:
        List of faculty matches
    """
    tool = FacultySearchTool()
    return tool.search(query, n_results, min_similarity)