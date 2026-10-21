# Chat RAG Xperiun

Chat interno construído com arquitetura **RAG (Retrieval-Augmented Generation)** para a Xperiun Tecnologia S.A. Carrega os documentos internos da empresa (contratos, políticas de preço, fornecedores) e permite que times de vendas, pós-vendas, compliance, compras e lideranças façam perguntas em linguagem natural, recebendo respostas fundamentadas apenas nos trechos relevantes dos documentos — nunca inventadas.

A plataforma foi desenvolvida em **5 ondas incrementais**, cada uma visível e testável no próprio Streamlit: Ingestão, Chunking, visualização dos Chunks, Retrieval (busca semântica) e Generation (resposta com LLM).

## Por que RAG

Em vez de enviar o documento inteiro da empresa para a IA a cada pergunta, o sistema:
1. Quebra os documentos em pedaços pequenos (**chunks**)
2. Transforma cada chunk em um vetor numérico (**embedding**)
3. Na hora da pergunta, busca só os chunks mais parecidos semanticamente com ela (**retrieval**)
4. Envia só esses poucos chunks + a pergunta para o LLM, que responde com base neles (**generation**)

Isso traz respostas mais precisas, mais baratas e rastreáveis — o usuário sempre vê quais trechos fundamentaram a resposta.

## Arquitetura e stack

| Camada | Tecnologia |
|---|---|
| Interface / visualização | [Streamlit](https://streamlit.io/) |
| Orquestração RAG | [LangChain](https://www.langchain.com/) |
| Extração de documentos | `pypdf` (PDF), `python-docx` (Word) |
| Chunking | `RecursiveCharacterTextSplitter` — 350 caracteres, overlap de 40 |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector store | [ChromaDB](https://www.trychroma.com/) — efêmero, roda localmente sem precisar instalar/gerenciar um banco |
| Geração de resposta | API da Anthropic — **Claude Sonnet 5** |
| Linguagem | Python 3.11+ |

### Fluxo das 5 ondas

```
docs/*.pdf, *.docx
       │
       ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────────┐
│ 1-2. Ingestão &  │───▶│ 3. Chunks    │───▶│ 4. Retrieval         │
│    Chunking      │    │ (visualização│    │ (busca semântica,   │
│ (pypdf/docx →    │    │  e inspeção) │    │  top-3, sem LLM)     │
│  350 chars/40 ov.)│    └──────────────┘    └──────────┬───────────┘
└──────────────────┘                                     │
                                                          ▼
                                           ┌──────────────────────────┐
                                           │ 5. Generation              │
                                           │ system prompt + pergunta + │
                                           │ chunks → Claude Sonnet 5   │
                                           └──────────────────────────┘
```

Cada aba do Streamlit corresponde a uma onda e mostra o resultado daquela etapa antes de avançar para a próxima — incluindo, na etapa de Generation, **sempre exibir os chunks usados antes da resposta final**, para permitir auditar se a busca semântica funcionou.

## Estrutura do projeto

```
.
├── app.py                  # Streamlit - UI das 5 ondas
├── requirements.txt
├── .env.example             # template das variáveis de ambiente
├── src/
│   ├── config.py            # carrega .env, parâmetros (chunk size, overlap, top-k, modelo)
│   ├── ingestion.py         # extrai texto de PDF/DOCX em docs/
│   ├── chunking.py          # RecursiveCharacterTextSplitter (350/40)
│   ├── embeddings.py        # wrapper OpenAI text-embedding-3-small
│   ├── vectorstore.py       # client e vectorstore Chroma
│   ├── retriever.py         # busca semântica top-k
│   └── generation.py        # system prompt + chamada à API Anthropic
├── docs/                    # documentos-fonte da Xperiun (PDFs/DOCX) — fonte da verdade do RAG
├── contexto/                # contexto institucional da Xperiun (não entra no RAG)
├── PRD.md                   # requisitos de produto
├── SPEC.md                  # especificação técnica das 5 ondas
└── Agents.md                # regras de orquestração do projeto
```

## Pré-requisitos

- **Python 3.11+** (importante: a versão do ChromaDB usada aqui não tem wheel pré-compilada para Python 3.12 no Windows — veja [Notas técnicas](#notas-técnicas-e-decisões-de-implementação))
- Chave de API da **OpenAI** (para embeddings)
- Chave de API da **Anthropic** (para geração de resposta)

## Instalação

```bash
# 1. Crie e ative um ambiente virtual isolado
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (Git Bash)
source .venv/Scripts/activate
# Linux/Mac
source .venv/bin/activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure as variáveis de ambiente
cp .env.example .env
# edite o .env e preencha OPENAI_API_KEY e ANTHROPIC_API_KEY
```

### Variáveis de ambiente (`.env`)

| Variável | Descrição | Default |
|---|---|---|
| `OPENAI_API_KEY` | Chave da OpenAI, usada só para gerar embeddings | — |
| `ANTHROPIC_API_KEY` | Chave da Anthropic, usada na etapa de Generation | — |
| `ANTHROPIC_MODEL` | Modelo Claude usado para gerar a resposta | `claude-sonnet-5` |
| `CHUNK_SIZE` | Tamanho de cada chunk, em caracteres | `350` |
| `CHUNK_OVERLAP` | Overlap entre chunks consecutivos, em caracteres | `40` |
| `TOP_K` | Quantidade de chunks retornados na busca semântica | `3` |
| `DOCS_DIR` | Pasta com os documentos-fonte | `docs` |

## Como rodar

```bash
streamlit run app.py
```

Acesse `http://localhost:8501` e navegue pelas abas na ordem:

1. **Ingestão & Chunking** — confirma quantos arquivos/páginas foram lidos de `docs/`
2. **Chunks** — mostra o total de chunks gerados e permite inspecionar o conteúdo de cada um
3. **Retrieval** — digite uma pergunta e veja os 3 chunks mais similares (busca semântica pura, sem IA)
4. **Generation** — digite a pergunta e veja os chunks usados como contexto, seguidos da resposta do Claude Sonnet 5

## Notas técnicas e decisões de implementação

Algumas decisões não óbvias tomadas durante o desenvolvimento, documentadas para quem for dar manutenção:

- **Python 3.11, não 3.12**: `chroma-hnswlib` (dependência do ChromaDB) não publica wheel pré-compilada para Windows + Python 3.12. Compilar do zero exigiria o Microsoft C++ Build Tools. Usar 3.11 evita essa dependência extra.
- **`numpy==1.26.4` e `pyarrow==17.0.0` fixados**: o LangChain 0.3.x exige `numpy<2` em Python <3.12, mas versões recentes do PyArrow (usado pelo Streamlit) exigem `numpy>=2`. As versões fixadas no `requirements.txt` são compatíveis entre si.
- **`import chromadb` antes do `streamlit`/`pyarrow` em `app.py`**: no Windows, as DLLs nativas do ChromaDB e do PyArrow entram em conflito dependendo da ordem de carregamento. Importar o ChromaDB primeiro evita um segfault na inicialização.
- **`chromadb.PersistentClient` em diretório temporário, não `EphemeralClient`**: o modo "em memória" do ChromaDB no Windows guarda a conexão SQLite em `threading.local()` — como o Streamlit reexecuta o script em threads diferentes a cada interação, a conexão criada numa thread é descartada quando a thread termina, destruindo o banco compartilhado em memória e causando `OperationalError: no such table: collections`. Usar um `PersistentClient` apontando para uma pasta temporária (criada via `tempfile.mkdtemp()`) resolve isso sem precisar instalar nenhum banco externo — a pasta não sobrevive ao fim da sessão de trabalho.
- **Client Chroma único e compartilhado**: `src/vectorstore.py` + `app.py` garantem que só existe um client ChromaDB por processo (via `st.cache_resource`), evitando múltiplos clients concorrentes competindo pela criação das tabelas internas.

## Fonte da verdade

Por instrução do `Agents.md`, qualquer execução segue a ordem **PRD → SPEC → `docs/` → `contexto/`**, e o sistema nunca inventa informação: quando a resposta não está nos chunks recuperados, o Claude é instruído a dizer explicitamente que não encontrou a informação nos documentos disponíveis.
