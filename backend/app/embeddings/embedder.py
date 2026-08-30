"""
Local embedding generation using Hugging Face Sentence Transformers.

We deliberately use a small local model (all-MiniLM-L6-v2, 384 dims) so
the app works fully offline / without any paid embedding API, per the
project's architecture requirements.
"""
from functools import lru_cache
from typing import List

import numpy as np

from app.core.config import settings


@lru_cache(maxsize=1)
def _get_model():
    # Imported lazily so the rest of the app (and tests that don't need
    # embeddings) can start up fast without pulling in torch immediately.
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.EMBEDDING_MODEL)


def embed_text(text: str) -> List[float]:
    """Embed a single piece of text into a fixed-size vector."""
    if not text or not text.strip():
        return [0.0] * settings.EMBEDDING_DIM
    model = _get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Batch-embed multiple texts (more efficient than one-by-one)."""
    if not texts:
        return []
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in np.atleast_2d(vectors)]


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Cosine similarity between two vectors already normalized or not."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)
