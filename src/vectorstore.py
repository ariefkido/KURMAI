# src/vectorstore.py
import logging
from typing import Optional
import google.generativeai as genai
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import config

logger = logging.getLogger(__name__)


class GeminiEmbeddings(Embeddings):
    """Wrapper langsung ke google-generativeai untuk hindari bug v1beta."""

    def __init__(self, api_key: str, model: str):
        genai.configure(api_key=api_key)
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = []
        for text in texts:
            r = genai.embed_content(model=self.model, content=text)
            result.append(r["embedding"])
        return result

    def embed_query(self, text: str) -> list[float]:
        r = genai.embed_content(model=self.model, content=text)
        return r["embedding"]


def build_vectorstore(
    documents: list[Document],
    api_key: str,
) -> Optional[FAISS]:
    if not documents:
        logger.error("Tidak ada dokumen untuk diindeks.")
        return None

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Total chunks: {len(chunks)}")

    embeddings = GeminiEmbeddings(api_key=api_key, model=config.EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    logger.info("FAISS index berhasil dibangun.")
    return vectorstore


def get_retriever(vectorstore: FAISS):
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": config.TOP_K},
    )
