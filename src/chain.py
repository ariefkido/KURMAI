# src/chain.py
# ============================================================
# RAG chain: retrieval + prompt + Gemini LLM
# ============================================================

import logging
from typing import Generator

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Anda adalah KURMAI, asisten resmi yang menjawab pertanyaan berdasarkan peraturan yang telah ditetapkan.

ATURAN PENTING:
1. Jawab HANYA berdasarkan konteks peraturan yang diberikan di bawah.
2. Jika informasi tidak ada dalam konteks, katakan dengan jelas bahwa informasi tersebut tidak tersedia dalam peraturan yang dimuat — jangan mengarang jawaban.
3. Sebutkan pasal atau sumber yang relevan saat menjawab.
4. Gunakan bahasa Indonesia yang formal dan mudah dipahami.
5. Jika pertanyaan tidak berkaitan dengan peraturan yang tersedia, sampaikan dengan sopan bahwa Anda hanya dapat menjawab seputar peraturan yang dimuat.

KONTEKS PERATURAN:
{context}
"""

HUMAN_TEMPLATE = "{question}"


def _format_docs(docs: list[Document]) -> str:
    """Format retrieved documents menjadi string konteks."""
    parts = []
    for doc in docs:
        meta = doc.metadata
        label = meta.get("label", "")
        bab = meta.get("bab", "")
        pasal = meta.get("pasal", "")
        judul_bab = meta.get("judul_bab", "")
        source_parts = [label]
        if bab:
            source_parts.append(f"BAB {bab}")
        if judul_bab:
            source_parts.append(judul_bab)
        if pasal:
            source_parts.append(f"Pasal {pasal}")
        source_info = " | ".join(source_parts)
        parts.append(f"[{source_info}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def build_chain(retriever, api_key: str):
    """
    Buat RAG chain.
    Return: callable chain yang menerima {"question": str}
    """
    llm = ChatGoogleGenerativeAI(
        model=config.GEMINI_MODEL,
        google_api_key=api_key,
        temperature=0.1,
        streaming=True,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_TEMPLATE),
    ])

    chain = (
        {
            "context": retriever | _format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


def stream_answer(chain, question: str) -> Generator[str, None, None]:
    """Stream jawaban token per token."""
    for chunk in chain.stream(question):
        yield chunk
