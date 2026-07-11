"""
FastEmbed embedding client wrapper.
Generates local vector embeddings using BAAI/bge-small-en-v1.5.
"""

from fastembed import TextEmbedding

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class FastEmbedClient:
    """
    Wrapper around FastEmbed TextEmbedding.
    Generates 384-dimensional vector embeddings locally.
    """

    def __init__(self) -> None:
        self._model = None
        try:
            logger.info(f"Initializing FastEmbed model: {settings.FASTEMBED_MODEL}")
            self._model = TextEmbedding(model_name=settings.FASTEMBED_MODEL)
        except Exception as e:
            logger.error(f"Failed to load FastEmbed model: {e}")

    def embed_query(self, query: str) -> list[float]:
        """Generate a single vector embedding for a query string."""
        if not self._model:
            # Fallback to dummy vector of size 384
            return [0.0] * settings.QDRANT_VECTOR_SIZE
        
        try:
            embeddings = list(self._model.embed([query]))
            # Return first embedding as a list of floats
            return list(map(float, embeddings[0].tolist()))
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return [0.0] * settings.QDRANT_VECTOR_SIZE

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Generate vector embeddings for a list of document strings."""
        if not self._model:
            return [[0.0] * settings.QDRANT_VECTOR_SIZE for _ in documents]
        
        try:
            embeddings = list(self._model.embed(documents))
            return [list(map(float, emb.tolist())) for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating list of embeddings: {e}")
            return [[0.0] * settings.QDRANT_VECTOR_SIZE for _ in documents]


# Client singleton
fastembed_client = FastEmbedClient()
