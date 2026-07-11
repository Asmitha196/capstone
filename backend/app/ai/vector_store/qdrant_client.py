"""
Qdrant vector database client wrapper.
Handles collection creation, document indexing, and similarity searches.
Supports mock fallback for local testing stability.
"""

from qdrant_client import QdrantClient as RealQdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class QdrantVectorStore:
    """
    Wrapper around QdrantClient for managing job and resume vector collections.
    """

    def __init__(self) -> None:
        self._client = None
        self.is_active = False

        try:
            if settings.QDRANT_URL:
                logger.info(f"Connecting to Qdrant Cloud at {settings.QDRANT_URL}...")
                self._client = RealQdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY,
                    timeout=5.0,
                )
            else:
                logger.info(f"Connecting to local Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}...")
                self._client = RealQdrantClient(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT,
                    api_key=settings.QDRANT_API_KEY,
                    timeout=5.0,
                )
            # Test connection
            self._client.get_collections()
            self.is_active = True
            logger.info("Connected to Qdrant successfully.")
            self._init_collections()
        except Exception as e:
            logger.warning(f"Could not connect to Qdrant: {e}. Vector operations will use mock fallback.")

    def _init_collections(self) -> None:
        """Initialize necessary collections if they don't exist."""
        if not self._client or not self.is_active:
            return

        for collection_name in [settings.QDRANT_COLLECTION_JOBS, settings.QDRANT_COLLECTION_RESUMES]:
            try:
                self._client.get_collection(collection_name)
                logger.debug(f"Qdrant collection '{collection_name}' already exists.")
            except (UnexpectedResponse, Exception):
                logger.info(f"Creating Qdrant collection '{collection_name}'...")
                try:
                    self._client.create_collection(
                        collection_name=collection_name,
                        vectors_config=models.VectorParams(
                            size=settings.QDRANT_VECTOR_SIZE,
                            distance=models.Distance.COSINE,
                        ),
                    )
                    logger.info(f"Qdrant collection '{collection_name}' created.")
                except Exception as ex:
                    logger.error(f"Error creating collection '{collection_name}': {ex}")

    async def upsert_points(self, collection_name: str, points: list[models.PointStruct]) -> bool:
        """Upsert a list of vector points into a Qdrant collection."""
        if not self._client or not self.is_active:
            return False

        try:
            self._client.upsert(collection_name=collection_name, points=points)
            return True
        except Exception as e:
            logger.error(f"Failed to upsert points to Qdrant collection {collection_name}: {e}")
            return False

    async def search_similarity(
        self, collection_name: str, query_vector: list[float], limit: int = 5
    ) -> list[models.ScoredPoint]:
        """Query Qdrant for top similarity matches."""
        if not self._client or not self.is_active:
            return []

        try:
            results = self._client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            return results
        except Exception as e:
            logger.error(f"Error during Qdrant similarity search: {e}")
            return []


# Vector Store singleton
qdrant_vector_store = QdrantVectorStore()
