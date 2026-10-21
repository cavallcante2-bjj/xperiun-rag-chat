"""Embeddings OpenAI text-embedding-3-small (SPEC.md - Onda 2)."""
from langchain_openai import OpenAIEmbeddings

from src import config


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=config.EMBEDDING_MODEL, api_key=config.OPENAI_API_KEY)
