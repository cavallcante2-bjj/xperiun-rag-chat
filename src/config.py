"""Configuração central do projeto, carregada do .env (SPEC.md)."""
from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / os.getenv("DOCS_DIR", "docs")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")

EMBEDDING_MODEL = "text-embedding-3-small"

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "350"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "40"))
TOP_K = int(os.getenv("TOP_K", "3"))
