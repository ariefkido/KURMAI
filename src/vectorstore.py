# src/vectorstore.py
import logging
from typing import Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import config

logger = logging.getLogger(__name__)


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

    embeddings = GoogleGenerativeAIEmbeddings(model=config.EMBEDDING_MODEL, google_api_key=api_key)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    logger.info("FAISS index berhasil dibangun.")
    return vectorstore


def get_retriever(vectorstore: FAISS):
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": config.TOP_K},
    )
