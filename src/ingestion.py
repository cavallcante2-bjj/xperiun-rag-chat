"""Carrega os documentos-fonte de docs/ (SPEC.md - Onda 2)."""
from pathlib import Path

import docx
from langchain_core.documents import Document
from pypdf import PdfReader


def _load_pdf(path: Path) -> list[Document]:
    reader = PdfReader(str(path))
    docs = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            docs.append(
                Document(
                    page_content=text,
                    metadata={"source": path.name, "page": page_num},
                )
            )
    return docs


def _load_docx(path: Path) -> list[Document]:
    document = docx.Document(str(path))
    text = "\n".join(p.text for p in document.paragraphs if p.text.strip())
    if not text.strip():
        return []
    return [Document(page_content=text, metadata={"source": path.name, "page": 1})]


def load_documents(docs_dir: Path) -> list[Document]:
    """Lê todos os PDFs e DOCX de docs_dir. Levanta aviso (não exceção) para
    arquivos sem texto extraível (ex.: PDF escaneado sem OCR)."""
    documents: list[Document] = []
    warnings: list[str] = []

    for path in sorted(docs_dir.iterdir()):
        if path.suffix.lower() == ".pdf":
            loaded = _load_pdf(path)
        elif path.suffix.lower() == ".docx":
            loaded = _load_docx(path)
        else:
            continue

        if not loaded:
            warnings.append(
                f"'{path.name}' não teve texto extraído (pode ser PDF escaneado sem OCR)."
            )
        documents.extend(loaded)

    return documents, warnings
