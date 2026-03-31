# src/vectorstore.py
# ============================================================
# Build FAISS vector store dari dokumen peraturan
# ============================================================

import logging
from typing import Optional

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

import config

logger = logging.getLogger(__name__)


def build_vectorstore(
    documents: list[Document],
    api_key: str,
) -> Optional[FAISS]:
    """
    Terima list Document, chunk, embed, kembalikan FAISS retriever.
    Return None jika documents kosong.
    """
    if not documents:
        logger.error("Tidak ada dokumen untuk diindeks.")
        return None

    # Chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Total chunks: {len(chunks)}")

    # Embedding
    embeddings = GoogleGenerativeAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        google_api_key=api_key,
    )

    # Build FAISS index (in-memory)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    logger.info("FAISS index berhasil dibangun.")
    return vectorstore


def get_retriever(vectorstore: FAISS):
    """Kembalikan retriever dengan TOP_K dari config."""
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": config.TOP_K},
    )
