"""Chat RAG Xperiun - plataforma de visualização por etapa (SPEC.md)."""
import chromadb  # noqa: F401  (precisa carregar antes do pyarrow/streamlit - conflito de DLL no Windows)
import pandas as pd
import streamlit as st

from src import config
from src.chunking import chunk_documents
from src.generation import generate_answer
from src.ingestion import load_documents
from src.retriever import search
from src.vectorstore import build_vectorstore, get_chroma_client

st.set_page_config(page_title="Chat RAG Xperiun", layout="wide")
st.title("Chat RAG Xperiun")
st.caption("Plataforma de visualização das etapas do RAG — Ingestão, Chunks, Retrieval e Generation.")

tab_ingestao, tab_chunks, tab_retrieval, tab_generation = st.tabs(
    ["1-2. Ingestão & Chunking", "3. Chunks", "4. Retrieval (Augmented)", "5. Generation"]
)


@st.cache_data(show_spinner="Lendo documentos e gerando chunks...")
def _run_ingestion_and_chunking():
    docs, warnings = load_documents(config.DOCS_DIR)
    chunks = chunk_documents(docs)
    return docs, warnings, chunks


@st.cache_resource
def _get_chroma_client():
    return get_chroma_client()


@st.cache_resource(show_spinner="Gerando embeddings e indexando no Chroma (em memória)...")
def _get_vectorstore(_chunks):
    return build_vectorstore(_chunks, client=_get_chroma_client())


docs, ingestion_warnings, chunks = _run_ingestion_and_chunking()

with tab_ingestao:
    st.subheader("Ingestão & Chunking")
    st.info(f"Fonte dos documentos: `{config.DOCS_DIR}`")
    st.write(f"Chunk size: {config.CHUNK_SIZE} caracteres | Overlap: {config.CHUNK_OVERLAP} caracteres")

    for w in ingestion_warnings:
        st.warning(w)

    arquivos = sorted({d.metadata["source"] for d in docs})
    col1, col2 = st.columns(2)
    col1.metric("Arquivos processados", len(arquivos))
    col2.metric("Páginas/partes extraídas", len(docs))
    st.write("Arquivos:", ", ".join(arquivos) if arquivos else "nenhum")

with tab_chunks:
    st.subheader("Visualização dos Chunks")
    st.metric("Total de chunks gerados", len(chunks))

    df = pd.DataFrame(
        [
            {
                "chunk_id": c.metadata["chunk_id"],
                "fonte": c.metadata["source"],
                "página": c.metadata["page"],
                "tamanho": len(c.page_content),
                "preview": c.page_content[:80].replace("\n", " ") + "...",
            }
            for c in chunks
        ]
    )

    selected_id = st.selectbox("Selecione um chunk para inspecionar", df["chunk_id"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    chunk_selecionado = chunks[selected_id]
    st.markdown(f"**Chunk {selected_id}** — fonte: `{chunk_selecionado.metadata['source']}` "
                f"(página {chunk_selecionado.metadata['page']}, {len(chunk_selecionado.page_content)} caracteres)")
    st.text_area("Conteúdo completo", chunk_selecionado.page_content, height=200)

def _render_chunks_resultado(results):
    for doc, score in results:
        with st.expander(
            f"chunk_id {doc.metadata['chunk_id']} — {doc.metadata['source']} "
            f"(p.{doc.metadata['page']}) — distância: {score:.4f}"
        ):
            st.text(doc.page_content)


with tab_retrieval:
    st.subheader("Busca Semântica (sem LLM)")
    st.write(f"Top-K: {config.TOP_K} | distância menor = mais similar")

    pergunta_retrieval = st.text_input("Digite sua pergunta", key="retrieval_question")
    if st.button("Buscar chunks", key="btn_retrieval") and pergunta_retrieval:
        vectorstore = _get_vectorstore(chunks)
        st.session_state["retrieval_results"] = search(vectorstore, pergunta_retrieval)

    if "retrieval_results" in st.session_state:
        st.markdown(f"**{len(st.session_state['retrieval_results'])} chunks mais similares:**")
        _render_chunks_resultado(st.session_state["retrieval_results"])

with tab_generation:
    st.subheader("Generation")
    st.write(f"Modelo: {config.ANTHROPIC_MODEL}")

    pergunta_gen = st.text_input("Digite sua pergunta", key="gen_question")
    if st.button("Perguntar", key="btn_gen") and pergunta_gen:
        vectorstore = _get_vectorstore(chunks)
        resultados = search(vectorstore, pergunta_gen)
        st.session_state["gen_results"] = resultados
        st.session_state["gen_question_feita"] = pergunta_gen
        with st.spinner(f"Chamando {config.ANTHROPIC_MODEL}..."):
            st.session_state["gen_answer"] = generate_answer(
                pergunta_gen, [doc for doc, _ in resultados]
            )

    if "gen_results" in st.session_state:
        st.markdown(f"**Pergunta:** {st.session_state['gen_question_feita']}")
        st.markdown(f"**{len(st.session_state['gen_results'])} chunks usados como contexto:**")
        _render_chunks_resultado(st.session_state["gen_results"])

        st.markdown("### Resposta")
        st.write(st.session_state["gen_answer"])
