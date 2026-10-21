"""Busca semântica pura (sem LLM) - SPEC.md Onda 4."""
from langchain_chroma import Chroma
from langchain_core.documents import Document

from src import config


def search(vectorstore: Chroma, query: str, k: int | None = None) -> list[tuple[Document, float]]:
    """Retorna os k chunks mais similares com a distância (menor = mais similar)."""
    k = k or config.TOP_K
    return vectorstore.similarity_search_with_score(query, k=k)
