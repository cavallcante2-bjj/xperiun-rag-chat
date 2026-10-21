"""Vetorstore Chroma (SPEC.md - Onda 4)."""
import tempfile

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.embeddings import get_embeddings


def get_chroma_client() -> chromadb.ClientAPI:
    """PersistentClient num diretório temporário (apagado quando o sistema
    limpar a pasta temp - não sobrevive além da sessão de trabalho, sem
    precisar instalar nenhum banco vetorial, como pede o SPEC.md).

    Não usamos chromadb.EphemeralClient() porque, no Windows, seu backend
    SQLite 'file::memory:?cache=shared' guarda a conexão em threading.local()
    (LockPool). Como o Streamlit executa cada rerun em threads diferentes, a
    conexão que criou as tabelas é coletada quando a thread termina, e o
    banco compartilhado em memória é destruído -> a próxima thread abre um
    banco vazio e qualquer query falha com 'no such table: collections'.
    Um PersistentClient grava em disco, então os dados sobrevivem à troca de
    thread."""
    tmp_dir = tempfile.mkdtemp(prefix="chroma_xperiun_")
    return chromadb.PersistentClient(path=tmp_dir)


def build_vectorstore(chunks: list[Document], client: chromadb.ClientAPI) -> Chroma:
    return Chroma.from_documents(documents=chunks, embedding=get_embeddings(), client=client)
