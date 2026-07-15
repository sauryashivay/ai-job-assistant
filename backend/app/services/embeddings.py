from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def create_embedding(text: str) -> list[float]:
    cleaned_text = text.strip()

    if not cleaned_text:
        return []

    model = get_embedding_model()

    embedding = model.encode(
        cleaned_text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def calculate_semantic_similarity(
    first_text: str,
    second_text: str,
) -> float:
    if not first_text.strip() or not second_text.strip():
        return 0.0

    model = get_embedding_model()

    embeddings = model.encode(
        [first_text, second_text],
        normalize_embeddings=True,
    )

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]],
    )[0][0]

    return float(max(0.0, min(similarity, 1.0)))