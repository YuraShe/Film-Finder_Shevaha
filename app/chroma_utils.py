import chromadb
from sentence_transformers import SentenceTransformer
from typing import Optional, Any

try:
    from . import config
except ImportError:  # pragma: no cover - fallback for direct script-style imports
    import config

_embedder: Optional[SentenceTransformer] = None
_chroma_client: Optional[Any] = None
_movie_collection: Optional[Any] = None


def get_embedder() -> SentenceTransformer:
    """Vytvoří a uloží do cache instanci embedovacího modelu sentence-transformers."""
    global _embedder

    if _embedder is None:
        _embedder = SentenceTransformer(
            config.EMBEDDING_MODEL,
            cache_folder=str(config.SENTENCE_TRANSFORMERS_HOME),
        )

    return _embedder


def get_chroma_collection():
    """Vytvoří a uloží do cache handle na cílovou Chroma kolekci."""
    global _chroma_client, _movie_collection

    if _chroma_client is None:
        if config.CHROMA_HOST:
            _chroma_client = chromadb.HttpClient(
                host=config.CHROMA_HOST,
                port=config.CHROMA_PORT,
            )
        else:
            _chroma_client = chromadb.PersistentClient(path=config.CHROMA_PATH)

    if _movie_collection is None:
        _movie_collection = _chroma_client.get_or_create_collection(
            name=config.COLLECTION_NAME
        )

    return _movie_collection


def search_movies(user_query: str, n_results: int = 5) -> list[dict]:
    """Prohledá kolekci filmů podle podobnosti embeddingů a vrátí výsledky."""
    user_query = (user_query or "").strip()
    if not user_query:
        return []

    embedder = get_embedder()
    collection = get_chroma_collection()

    query_embedding = embedder.encode(
        [user_query],
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    hits: list[dict] = []
    ids = results.get("ids", [[]])
    documents = results.get("documents", [[]])
    metadatas = results.get("metadatas", [[]])
    distances = results.get("distances", [[]])

    if not ids or not ids[0]:
        return []

    for i in range(len(ids[0])):
        metadata = metadatas[0][i] or {}
        hits.append(
            {
                "id": ids[0][i],
                "title": metadata.get("title", "Unknown title"),
                "year": metadata.get("year", "unknown"),
                "distance": distances[0][i] if distances and distances[0] else None,
                "document": documents[0][i] if documents and documents[0] else "",
                "metadata": metadata,
            }
        )

    return hits