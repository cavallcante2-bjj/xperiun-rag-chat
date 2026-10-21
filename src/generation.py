"""Generation: system prompt + pergunta + chunks -> Claude (SPEC.md Onda 5)."""
from anthropic import Anthropic
from langchain_core.documents import Document

from src import config

SYSTEM_PROMPT = """Você é o assistente interno da Xperiun Tecnologia S.A. (Xperiun Cloud Solutions), \
usado pelos times de vendas, pós-vendas, compliance, compras e lideranças técnicas e não técnicas.

Você responde dúvidas sobre gestão de contratos e reajustes, políticas de preços, política de \
fornecedores e demais assuntos do time de receita.

Regras obrigatórias:
- Responda SOMENTE com base nos trechos de documentos fornecidos no contexto abaixo. Nunca invente \
informações que não estejam explicitamente nos trechos.
- Se a resposta não estiver nos trechos fornecidos, diga claramente: "Não encontrei essa informação \
nos documentos disponíveis." Não tente adivinhar.
- Seja direto, objetivo e em português.
- Quando a informação vier de um trecho específico, mencione de qual documento-fonte ela foi extraída.
"""


def _build_context(chunks: list[Document]) -> str:
    parts = [
        f"[Fonte: {c.metadata.get('source')}, página {c.metadata.get('page')}]\n{c.page_content}"
        for c in chunks
    ]
    return "\n\n---\n\n".join(parts)


def generate_answer(question: str, chunks: list[Document]) -> str:
    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    context = _build_context(chunks)
    user_message = f"Contexto recuperado:\n\n{context}\n\nPergunta do usuário: {question}"

    response = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text
